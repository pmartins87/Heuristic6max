# Registro de decisões (ADR)

## ADR-001 — Heurística, não solver
Objetivo: NLHE cash 6-max próximo de princípios GTO por heurísticas auditáveis; não reivindicar equilíbrio matemático, EV ótimo ou winrate. Requisitos de validação diferentes de simplesmente passar testes unitários. **Válido.**

## ADR-002 — GitHub como fonte de verdade
Repositório: https://github.com/pmartins87/Heuristic6max. Toda revisão deve consultar e atualizar `README.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `CHANGELOG.md` e `HANDOFF.md`. Preservar versões e impedir documentação obsoleta. **Válido.**

## ADR-003 — v0.5 audita sem alterar v0.4
Vários agregados 4bet são menores que números ART/GTO; benchmark não tem árvore/rake exatamente idênticos. Não alterar percentuais cegamente. Adicionar decomposição e revisar as classes primeiro. **Válido. Mudança exige evidência de mão e contexto, não apenas agregado.**

## ADR-004 — Falha explícita
Política ausente retorna `None`, nunca Fold ou Check silencioso; range DRAFT não é estratégia pronta para mesa. **Válido.**

## ADR-005 — Escada de evidência
(1) testes unitários e replays sintéticos, (2) replay real e observação confiável, (3) auditoria estratégica/benchmark comparável, (4) teste de integração da ação final em OH. Sucesso em (1) não prova (2–4). **Válido.**

## ADR-006 — Preservar DeepCrusher/CrusherTBP
Projeto novo, sem importar decisões estratégicas antigas cegamente e sem modificar seus arquivos. **Válido.**