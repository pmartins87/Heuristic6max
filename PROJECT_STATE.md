# Estado atual — Heuristic6max
**Data:** 20/11/2026 | **Checkpoint:** v0.6.1 G2-a | **Estado estratégico:** HOLD / não operacional.

## Evidências concluídas
- G0: arquitetura e contratos.
- G1: reconstrução e observações **sintéticas**; replays reais do OpenHoldem continuam pendentes.
- G2: RFI 5 × 169 = 845 registros; VS_OPEN 15 × 169 = 2.535; VS_3BET 15 × 169 = 2.535. Todos DRAFT, sem avaliação completa de EV.
- v0.5: 119 testes e decomposição de 4-bet por mão; sem modificar a estratégia da v0.4.
- v0.6: 124 testes locais aprovados; card removal físico nas 1.326 combinações com modelo de 3-bet VS_OPEN; **nenhuma ação ou range foi alterado**. As frequências condicionais de 4-bet ficaram 0,409–1,766 p.p. abaixo dos agregados antigos nos 15 nós.
- Dos oito nós originalmente MAJOR_REVIEW, sete ainda têm diferenças superiores a 8 p.p. frente à referência publicada após novo condicionamento; BTN–SB apresenta 6,09 p.p. **Os benchmarks têm rake/árvores diferentes; não validam EV nem autorizam ajustes automáticos.**

## Integridade no GitHub
- v0.5 completo em [gto6_heuristic_v0_5/](gto6_heuristic_v0_5/) — 51 arquivos.
- v0.6 histórica em [gto6_heuristic_v0_6/](gto6_heuristic_v0_6/) — 61 arquivos, com errata de manifesto.
- v0.6.1 corrente em [gto6_heuristic_v0_6_1/](gto6_heuristic_v0_6_1/) — 66 arquivos, incluindo verificação corrigida.
- **Errata v0.6:** 50 arquivos-base de conteúdo permaneceram idênticos; o arquivo SHA256SUMS.txt mudou corretamente após ser regerado, apesar do antigo CSV v0.6 ter marcado 51/51 SAME. A v0.6.1 corrige a trilha de integridade, sem alterar a estratégia.
- Reproduzir: cd gto6_heuristic_v0_6_1 && python -m unittest -q; depois python vs3_blocker_audit_v0_6.py. Verifique SHA256SUMS.txt **antes** de regerar qualquer CSV.

## Premissas e limitações
Cash 6-max, 100 BB alvo (95–105), blinds 0,5/1 BB, sem ante, RFI 2,5 BB LJ–BTN e 3 BB SB; sizings fixos de 3bet, sem limpers/callers/squeeze/short stacks, rake não calibrado. Não há estratégia pós-flop, VS_4BET/5BET ou integração operacional OpenHoldem. Nenhum resultado de simulação demonstra lucratividade real, proximidade quantitativa à GTO ou segurança em mesas.

## Próximo gate
G2-a permanece aberto: auditar a composição exata dos oito confrontos com premissas de rake/sizing e frequências de vilão coerentes antes de mudar ranges. Não iniciar VS_4BET até a decisão documentada. G1 exige replays reais em ambiente de teste sem apostas.
