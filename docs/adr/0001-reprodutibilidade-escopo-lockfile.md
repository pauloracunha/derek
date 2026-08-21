---
status: accepted
---

# Reprodutibilidade byte-idêntica é escopada ao lockfile, não a upgrades futuros

`networkx.community.louvain_communities` e outras rotinas estocásticas do pipeline aceitam `seed` inteiro, mas o guia de migração do NetworkX (NXEP 4) documenta que, desde a troca do gerador aleatório padrão para `numpy.random.Generator`, um inteiro como seed não garante mais resultado idêntico entre versões da biblioteca — só um `numpy.random.RandomState` explícito garantiria isso de forma duradoura.

Decidimos que "reprodutibilidade byte-idêntica" (Constitution Princípio VI, FR-018) vale **dentro da mesma versão travada em `uv.lock`**, não através de upgrades futuros de dependências. Usamos `seed=42` (inteiro) em todo o pipeline, sem `RandomState` explícito. Se o `networkx` for atualizado no futuro e a reprodutibilidade quebrar, isso é esperado e não é um bug — é reprocessar com a nova versão travada.

Alternativa rejeitada: `numpy.random.RandomState` explícito em toda chamada estocástica, para garantir reprodutibilidade através de upgrades. Rejeitada por complexidade desproporcional ao escopo do projeto (livro de Atos, sem expectativa de manutenção de longo prazo).
