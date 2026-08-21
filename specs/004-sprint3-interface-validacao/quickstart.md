# Quickstart: Sprint 3 — Interface e Validação

## Rodar localmente

```bash
just data       # se ainda não rodou o pipeline
just sprint1
uv run python -m pipeline.s08_export   # gera os 4 JSONs em data/processed/
cp data/processed/*.json web/public/data/
just web        # cd web && npm run dev
```

Abrir `http://localhost:5173` (porta padrão do Vite).

## Verificar Princípio I (incerteza nunca colapsa) manualmente

1. Achar um lugar com 2+ candidatos: `jq '[.[] | select(.candidate_count >= 2)] | .[0]' web/public/data/places.json`
2. Selecioná-lo na UI.
3. Confirmar visualmente que todos os candidatos aparecem no mapa ao mesmo tempo, com
   opacidade/tamanho diferentes.

## Verificar Princípio II (não-localizável nunca desaparece)

1. Contar total esperado: `jq '[.[] | select(.is_locatable == false)] | length' web/public/data/places.json`
2. Abrir painel de não-localizáveis na UI e contar itens — deve bater exatamente.

## Build de produção e publicação

```bash
cd web && npm run build   # gera web/dist
```

Publicar `web/dist` via GitHub Pages (decisão em `research.md` #4).

## Teste de compreensão (US5)

1. Publicar a aplicação (FR-009).
2. Recrutar 3–5 participantes que não conhecem o projeto.
3. Pedir para explorarem livremente, sem explicação prévia da equipe.
4. Perguntar: "por que alguns lugares aparecem com múltiplos pontos no mapa?"
5. Registrar resposta (correta/incorreta + justificativa) em `docs/usability-test.md`.
6. Calcular taxa de acerto e reportar no relatório final, mesmo se abaixo de 80%
   (Princípio VI).
