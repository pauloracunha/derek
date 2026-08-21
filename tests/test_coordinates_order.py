"""Constitution III: lonlat de origem é "longitude,latitude" — testado contra bbox real de Atos (docs/adr/0005)."""

from pipeline.config import BBOX_LAT, BBOX_LON


def test_all_candidates_fall_within_eastern_mediterranean_bbox(places):
    offenders = []
    for p in places:
        for c in p["candidates"]:
            if not (BBOX_LON[0] <= c["lon"] <= BBOX_LON[1]):
                offenders.append((p["place_id"], c["modern_id"], "lon", c["lon"]))
            if not (BBOX_LAT[0] <= c["lat"] <= BBOX_LAT[1]):
                offenders.append((p["place_id"], c["modern_id"], "lat", c["lat"]))
    assert not offenders, f"Coordenadas fora do bbox esperado (possível troca lon/lat): {offenders}"
