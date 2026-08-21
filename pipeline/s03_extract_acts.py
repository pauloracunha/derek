"""Extrai e normaliza os lugares de Atos.

Regras de negócio (com base em docs/data-contracts.md e os ADRs 0003/0004):

- Um Place entra no conjunto se tiver >=1 versículo com sort começando em BOOK_ID.
- Place.verses/chapters/mention_count são filtrados só a menções de Atos.
- candidates vem de modern_associations; probability usa clip-a-zero + fallback
  uniforme (ADR 0003) porque score pode ser negativo.
- is_locatable é decidido por candidates não-vazio, não pela presença de uma
  identificação `special` concorrente (ADR 0004).
- sources vem de identification_sources (nível Place, não por candidato).
"""

import json
import math
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import duckdb

from pipeline import config

KEPT_PRIORITY = ["unknown_place", "nonspecific_place", "multiple_locations"]


def _load_jsonl_by_id(path: Path) -> dict:
    result = {}
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            result[d["id"]] = d
    return result


def _atos_place_ids(con: duckdb.DuckDBPyConnection) -> set[str]:
    rows = con.execute(
        "SELECT id FROM ancient WHERE EXISTS "
        "(SELECT 1 FROM UNNEST(verses) AS t(v) WHERE v.sort LIKE ?)",
        [f"{config.BOOK_ID}%"],
    ).fetchall()
    return {r[0] for r in rows}


def _filter_atos_verses(verses: list[dict]) -> list[dict]:
    return [v for v in verses if v["sort"].startswith(config.BOOK_ID)]


def _resolve_candidate(
    place: dict, modern_id: str, assoc: dict, modern_by_id: dict
) -> dict:
    """Resolve lon/lat/lonlat_type. Nunca descarta um candidato silenciosamente (Constitution I):
    tenta as resoluções referenciadas, depois cai para modern.jsonl; se nada resolver, é erro alto."""
    modern_place = modern_by_id.get(modern_id)
    precision_meters = (
        modern_place.get("precision", {}).get("meters") if modern_place else None
    )

    lonlat_type = None
    for ident_i, res_j in assoc["identification_ids"]:
        try:
            res = place["identifications"][ident_i]["resolutions"][res_j]
        except (IndexError, KeyError):
            continue
        lonlat = res.get("lonlat")
        if lonlat:
            lon_str, lat_str = lonlat.split(",")
            return {
                "modern_id": modern_id,
                "name": assoc["name"],
                "lon": float(lon_str),
                "lat": float(lat_str),
                "score": assoc["score"],
                "lonlat_type": res.get("lonlat_type"),
                "precision_meters": precision_meters,
            }
        lonlat_type = lonlat_type or res.get("lonlat_type")

    # Fallback: coordenada própria do modern place (não encontrada em nenhuma resolução)
    if modern_place and modern_place.get("lonlat"):
        lon_str, lat_str = modern_place["lonlat"].split(",")
        return {
            "modern_id": modern_id,
            "name": assoc["name"],
            "lon": float(lon_str),
            "lat": float(lat_str),
            "score": assoc["score"],
            "lonlat_type": lonlat_type,
            "precision_meters": precision_meters,
        }

    raise ValueError(
        f"Candidato {modern_id} de {place.get('friendly_id')} ({place['id']}) sem lonlat em"
        " nenhuma resolução nem em modern.jsonl — nunca descartar silenciosamente (Constitution I)."
    )


def _normalize_probabilities(candidates: list[dict]) -> None:
    """Clip-a-zero + fallback uniforme (docs/adr/0003-normalizacao-score-negativo.md)."""
    clipped = [max(c["score"], 0) for c in candidates]
    total = sum(clipped)
    if total > 0:
        for c, s in zip(candidates, clipped):
            c["probability"] = s / total
    else:
        n = len(candidates)
        for c in candidates:
            c["probability"] = 1 / n if n else 0.0


def _dispersion_index(candidates: list[dict]) -> float:
    """Entropia normalizada da distribuição de probabilidade (0 = concentrada, 1 = uniforme)."""
    n = len(candidates)
    if n <= 1:
        return 0.0
    probs = [c["probability"] for c in candidates if c["probability"] > 0]
    entropy = -sum(p * math.log(p) for p in probs)
    max_entropy = math.log(n)
    return entropy / max_entropy if max_entropy > 0 else 0.0


def _resolve_locatability(place: dict, candidates: list[dict]) -> tuple[bool, str | None]:
    """Docs/adr/0004: candidates não-vazio decide is_locatable, não a presença de `special`."""
    if candidates:
        return True, None

    specials = {
        i.get("special")
        for i in place.get("identifications", [])
        if i.get("id_source") == "special"
    }
    for reason in KEPT_PRIORITY:
        if reason in specials:
            return False, reason
    if specials:
        # só sobrou razão "excludente" -> sinalizado para exclusão total (retorna None especial)
        return False, "__excluded__"
    return False, "no_candidates_resolved"


def _stringify_locator(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _extract_sources(place: dict, sources_by_id: dict) -> list[dict]:
    """Locator vem de identification_sources[source_id] — chaves observadas incluem tanto
    singular (title/page/map/table) quanto plural com lista (titles/pages), ver docs/data-contracts.md."""
    out = []
    for source_id, locator_obj in place.get("identification_sources", {}).items():
        src = sources_by_id.get(source_id)
        if src is None:
            continue
        first_value = next(iter(locator_obj.values()), None) if locator_obj else None
        locator = _stringify_locator(first_value) if first_value is not None else None
        out.append({
            "source_id": source_id,
            "citation": src.get("display_name", source_id),
            "locator": locator,
        })
    return out


def extract_place(place: dict, sources_by_id: dict, modern_by_id: dict) -> dict | None:
    verses = _filter_atos_verses(place.get("verses", []))
    if not verses:
        return None

    candidates = [
        _resolve_candidate(place, modern_id, assoc, modern_by_id)
        for modern_id, assoc in place.get("modern_associations", {}).items()
    ]
    _normalize_probabilities(candidates)

    is_locatable, special_reason = _resolve_locatability(place, candidates)
    if special_reason == "__excluded__":
        return None  # not_a_place / not_a_proper_name / recursive, sem candidato concorrente

    sorted_verses = sorted(verses, key=lambda v: v["sort"])
    chapters = sorted({int(v["sort"][2:5]) for v in sorted_verses})

    return {
        "place_id": place["id"],
        "name": place["friendly_id"],
        "slug": place["url_slug"],
        "type": place.get("type") or (place.get("types") or [None])[0],
        "is_locatable": is_locatable,
        "special_reason": special_reason,
        "verses": [v["sort"] for v in sorted_verses],
        "mention_count": len(sorted_verses),
        "chapters": chapters,
        "candidates": candidates,
        "candidate_count": len(candidates),
        "dispersion_index": _dispersion_index(candidates),
        "sources": _extract_sources(place, sources_by_id),
    }


def run() -> list[dict]:
    con = duckdb.connect(str(config.DUCKDB_PATH))
    try:
        atos_ids = _atos_place_ids(con)
    finally:
        con.close()

    ancient_by_id = _load_jsonl_by_id(config.RAW_DIR / "ancient.jsonl")
    sources_by_id = _load_jsonl_by_id(config.RAW_DIR / "source.jsonl")
    modern_by_id = _load_jsonl_by_id(config.RAW_DIR / "modern.jsonl")

    places = []
    for place_id in atos_ids:
        place = ancient_by_id[place_id]
        extracted = extract_place(place, sources_by_id, modern_by_id)
        if extracted is not None:
            places.append(extracted)

    places.sort(key=lambda p: p["place_id"])
    return places


THRESHOLD_PCT = 15.0
DISTRIBUTION_ARTIFACT_PATH = Path("docs/candidate-distribution.md")


def compute_candidate_distribution(places: list[dict]) -> dict:
    """Cálculo puro — decide o eixo narrativo do relatório (H1, definitions.md §5.1).
    Sem print nem write; ver print_candidate_distribution/write_distribution_artifact
    (grill 2026-08-02 Q1, specs/002-fechar-lacunas-sprint1)."""
    dist = Counter()
    for p in places:
        if not p["is_locatable"]:
            continue
        n = p["candidate_count"]
        dist["1"] += n == 1
        dist["2"] += n == 2
        dist["3+"] += n >= 3

    locatable = sum(1 for p in places if p["is_locatable"])
    unlocatable = sum(1 for p in places if not p["is_locatable"])
    total_locatable = locatable or 1
    multi = dist["2"] + dist["3+"]
    pct_multi = 100 * multi / total_locatable

    return {
        "locatable_count": locatable,
        "unlocatable_count": unlocatable,
        "with_1_candidate": dist["1"],
        "with_2_candidates": dist["2"],
        "with_3plus_candidates": dist["3+"],
        "multi_candidate_pct": pct_multi,
        "threshold_pct": THRESHOLD_PCT,
        "threshold_crossed": pct_multi >= THRESHOLD_PCT,
    }


def print_candidate_distribution(result: dict) -> None:
    print(f"Lugares de Atos localizáveis:        {result['locatable_count']}")
    print(
        f"Com 1 candidato:                     {result['with_1_candidate']}"
        f"  ({100 * result['with_1_candidate'] / (result['locatable_count'] or 1):.1f}%)"
    )
    print(
        f"Com 2 candidatos:                     {result['with_2_candidates']}"
        f"  ({100 * result['with_2_candidates'] / (result['locatable_count'] or 1):.1f}%)"
    )
    print(
        f"Com 3+ candidatos:                    {result['with_3plus_candidates']}"
        f"  ({100 * result['with_3plus_candidates'] / (result['locatable_count'] or 1):.1f}%)"
    )
    print(f"Não localizáveis (special):          {result['unlocatable_count']}")

    if result["threshold_crossed"]:
        print(
            f"\n{result['multi_candidate_pct']:.1f}% dos lugares localizáveis têm múltiplos"
            " candidatos — H1 sustentada."
        )
    else:
        print(
            f"\nATENÇÃO: só {result['multi_candidate_pct']:.1f}% dos lugares têm múltiplos"
            f" candidatos (<{result['threshold_pct']:.0f}%). H1 fraca — considerar pivotar o"
            " eixo para incerteza de precisão (lonlat_type)."
        )


def write_distribution_artifact(result: dict) -> None:
    """Fecha a lacuna de evidência R1.5 (specs/002-fechar-lacunas-sprint1) — persiste em
    arquivo o mesmo cálculo que print_candidate_distribution() imprime, sempre sobrescrevendo."""
    generated_at = datetime.now(UTC).isoformat()
    side = "ACIMA" if result["threshold_crossed"] else "ABAIXO"
    lines = [
        "# Distribuição de candidatos por lugar",
        "",
        (
            f"Gerado automaticamente por `pipeline/s03_extract_acts.py` em {generated_at}. "
            "Não editar à mão — reflete sempre a execução mais recente da extração."
        ),
        "",
        f"- Lugares de Atos localizáveis: {result['locatable_count']}",
        f"- Com 1 candidato: {result['with_1_candidate']}",
        f"- Com 2 candidatos: {result['with_2_candidates']}",
        f"- Com 3+ candidatos: {result['with_3plus_candidates']}",
        f"- Não localizáveis (special): {result['unlocatable_count']}",
        "",
        f"- `threshold_pct`: {result['threshold_pct']:.1f}",
        f"- `multi_candidate_pct`: {result['multi_candidate_pct']:.1f}",
        (
            f"- `threshold_crossed`: {result['threshold_crossed']} "
            f"({side} do limiar de {result['threshold_pct']:.0f}%)"
        ),
    ]
    DISTRIBUTION_ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    DISTRIBUTION_ARTIFACT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  Distribuição gravada em {DISTRIBUTION_ARTIFACT_PATH}")


def main() -> None:
    places = run()
    result = compute_candidate_distribution(places)
    print_candidate_distribution(result)
    write_distribution_artifact(result)
    print(f"\nTotal de lugares extraídos (locatable + not): {len(places)}")


if __name__ == "__main__":
    main()
