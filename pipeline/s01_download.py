"""Baixa as fontes brutas para data/raw/. Nunca modifica data/raw/ depois de baixado (Constitution V)."""

import io
import zipfile

import requests

from pipeline import config

USER_AGENT = "atlas-atos-pipeline/0.1 (+https://github.com/openbibleinfo/Bible-Geocoding-Data)"


def _download(url: str) -> bytes:
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.content


def download_geocoding_files() -> None:
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    for filename, url in config.SOURCES.items():
        dest = config.RAW_DIR / filename
        dest.write_bytes(_download(url))
        print(f"  {filename}: {dest.stat().st_size:,} bytes")


def download_cross_references() -> None:
    """A URL .txt direta dá 403 — o arquivo só existe dentro do .zip (ver docs/data-contracts.md)."""
    config.RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_bytes = _download(config.CROSS_REFERENCES_ZIP_URL)
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        content = zf.read(config.CROSS_REFERENCES_ZIP_MEMBER)
    dest = config.RAW_DIR / config.CROSS_REFERENCES_FILENAME
    dest.write_bytes(content)
    print(f"  {config.CROSS_REFERENCES_FILENAME}: {dest.stat().st_size:,} bytes")


def main() -> None:
    print("Baixando ancient.jsonl, modern.jsonl, source.jsonl...")
    download_geocoding_files()
    print("Baixando cross-references.zip e extraindo cross_references.txt...")
    download_cross_references()


if __name__ == "__main__":
    main()
