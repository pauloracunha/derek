set shell := ["bash", "-uc"]

# Baixa as fontes brutas (ancient.jsonl, modern.jsonl, source.jsonl, cross-references)
data:
    uv run python -m pipeline.s01_download

# TODO: reativar quando s04-s07 existirem — Sprint 2 (hoje falha, esses módulos não existem)
# pipeline:
#     uv run python -m pipeline.s01_download
#     uv run python -m pipeline.s02_load
#     uv run python -m pipeline.s03_extract_acts
#     uv run python -m pipeline.s04_build_graph
#     uv run python -m pipeline.s05_uncertainty
#     uv run python -m pipeline.s06_communities
#     uv run python -m pipeline.s07_linkpred
#     uv run python -m pipeline.s08_export

# Sprint 1 completa num comando só (download->carga->extração->exportação) — sem s04-s07
sprint1:
    uv run python -m pipeline.sprint1

# Roda a suíte de testes do pipeline (exclui testes lentos/rede real — ver `test-slow`)
test:
    uv run pytest tests/ -v -m "not slow"

# Roda só os testes lentos (rede real, ambiente limpo) — não faz parte do dia a dia
test-slow:
    uv run pytest tests/ -v -m "slow"

# Sobe o dev server do frontend
web:
    cd web && npm run dev

# Lint (python + web)
lint:
    uv run ruff check pipeline/ tests/
    cd web && npx eslint .
