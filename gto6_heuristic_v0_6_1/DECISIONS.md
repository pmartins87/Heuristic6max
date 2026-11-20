# Decisões técnicas — Heuristic6max

## ADR-001 — Objetivo: heurística próxima da GTO, não solver (2026-11-20)
A estratégia é de NLHE cash 6-max e busca aproximação de princípios GTO com ranges explícitos, história de ações e frequências mistas; não promete Nash, EV ótima nem winrate. Conclusões de benchmarks são comparativos condicionais, nunca prova de equivalência.

## ADR-002 — Fonte de verdade GitHub (2026-11-20)
O repositório `pmartins87/Heuristic6max` será a referência para roadmap, decisões, código, testes e estados. Cada revisão relevante deve reler e atualizar `README.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md` e `CHANGELOG.md`. Preservar histórico. Nenhum novo chat deve reconstruir o projeto apenas de memória.

## ADR-003 — Ranges v0.4 preservados em v0.5 (2026-11-20)
Oito nós VS_3BET apresentavam diferença agregada superior a 8 p.p. ante uma referência publicada. Como a árvore, o rake e a frequência de RFI não são idênticos, ajustar números automaticamente para se igualarem seria metodologicamente incorreto. A v0.5 faz auditoria de composição e deixa a calibração em HOLD. Reabrir mudança somente após revisar mãos, range adversário e ambiente de referência.

## ADR-004 — Nunca transformar falta de política em Fold/Check (2026-11-20)
A API de política devolve `None` quando contexto não está coberto. Não construir fallback operacional silencioso. Políticas DRAFT não são aprovação para jogar.

## ADR-005 — Critérios de evidência (2026-11-20)
Separar: (a) testes unitários e replays sintéticos de coerência, (b) replays reais de Observação/Estado, (c) avaliação estratégica contra benchmarks compatíveis, (d) teste de ações finais no OpenHoldem. Passar em (a) não conclui (b-d).
