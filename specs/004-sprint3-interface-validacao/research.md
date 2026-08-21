# Research: Sprint 3 — Interface e Validação

## 1. Test runner do frontend

**Decision**: Vitest + @testing-library/react.

**Rationale**: `web/` já usa Vite 8; Vitest reusa a mesma config/transform (TS, JSX) sem
duplicar setup. `@testing-library/react` testa componentes pelo comportamento visível
(o que renderiza), alinhado à necessidade de verificar Princípio I/II na prática (todos
os candidatos renderizados, todos os não-localizáveis listados).

**Alternatives considered**:
- Jest — exigiria config paralela de transform (ts-jest/babel) além da já existente do
  Vite; sem ganho sobre Vitest neste projeto.
- Playwright puro (sem unit) — bom para E2E do teste de compreensão, mas insuficiente
  para verificar unitariamente peso visual por candidato (US1) sem abrir browser real a
  cada run; mantido como opção complementar só para o fluxo E2E, não substitui Vitest.

## 2. Biblioteca de mapa

**Decision**: `maplibre-gl` (já presente em `package.json`).

**Rationale**: já é dependência instalada; suporta camadas de marcador com estilo
data-driven (`circle-opacity`, `circle-radius` por expressão), o que mapeia diretamente
para FR-002 (opacidade + tamanho proporcionais a `probability`) sem biblioteca adicional.

**Alternatives considered**: Leaflet — mais simples, mas MapLibre já escolhido e
instalado; trocar agora seria retrabalho sem justificativa.

## 3. Layout do grafo de coocorrência

**Decision**: `d3-force` (já presente em `package.json`), renderizado em SVG/Canvas
custom dentro de `NetworkGraph.tsx`.

**Rationale**: já instalado; simulação de força é adequada para grafo de ~107 nós/1059
arestas sem exigir biblioteca de grafo dedicada (ex. Cytoscape) para esse volume.

**Alternatives considered**: Cytoscape.js — mais recursos (agrupamento visual nativo por
comunidade), mas dependência nova não justificada para volume de dados pequeno; se o
agrupamento por comunidade (FR-005) ficar difícil de expressar só com d3-force, revisitar.

## 4. Hospedagem da aplicação publicada

**Decision**: GitHub Pages, a partir do build estático de `web/dist`.

**Rationale**: projeto não tem backend em runtime (constituição); GitHub Pages serve
estático direto do repositório sem custo e sem infraestrutura adicional, atende FR-009
(URL pública, sem cadastro/login).

**Alternatives considered**: Netlify/Vercel — equivalentes em capacidade; GitHub Pages
escolhido por já estar dentro do mesmo ecossistema do repositório, sem conta externa
adicional a gerenciar.

**Detalhe de configuração (grill 2026-08-19)**: repositório ainda não existe (projeto não
é git repo até o momento desta decisão). Preferência: nomear o repositório
`<usuário>.github.io` (user/org site) para que o Pages sirva na raiz (`base: '/'` no
`vite.config.ts`, sem subpasta) — mais simples que um project site, que exigiria
`base: '/<nome-do-repo>/'`. Se por qualquer motivo o repositório não puder usar esse nome
(ex. já existe outro projeto lá), cair para project site e setar `base` explicitamente
antes do primeiro `npm run build` de produção — deixar sem configurar quebra todos os
assets estáticos (JS/CSS/JSON) em produção.

## 5. Registro do teste de compreensão (US5)

**Decision**: markdown simples em `docs/usability-test.md`, uma tabela por participante
(data, acerto/erro, justificativa transcrita).

**Rationale**: amostra de 3–5 participantes (Assumptions de 001-atlas-atos) não justifica
ferramenta de pesquisa dedicada; markdown versionado no repositório é suficiente para
citação no relatório final (SC-003) e mantém consistência com o resto da documentação
do projeto (`docs/*.md`).

**Alternatives considered**: planilha externa (Google Sheets) — adiciona dependência
externa e risco de não ficar versionada/citável junto ao código; descartada.

## Resumo — NEEDS CLARIFICATION resolvidos

Nenhum item do Technical Context ficou como NEEDS CLARIFICATION após esta fase; todas as
decisões acima usam dependências já presentes no projeto ou ferramentas gratuitas sem
infraestrutura nova.
