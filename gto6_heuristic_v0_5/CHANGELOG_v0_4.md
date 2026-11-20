# GTO Heuristic 6-Max — Changelog v0.4

**20/11/2026 — Defesa VS_3BET (DRAFT / revisão necessária)**

## Acrescentado

1. `vs_3bet_reference.py`: 15 árvores opener×3bettor, 169 classes por árvore, cinco categorias de ação/mistura e ranges específicos por cenário; emitidas 2.535 linhas da matriz.
2. Alcance condicionado ao RFI: 888 registros com alguma possibilidade de open, 1.647 sem reachability; `policy_for` retorna `None` nas classes impossíveis.
3. `vs_3bet_bridge.py`: contrato de replay completo, cross-check do pote, do `to_call`, tamanho de 3-bet, relação IP/OOP, stacks e ações legais. Bloqueia squeeze, caller, shove e outros casos não modelados.
4. Sizing de 4-bet normal (**raise-to**), diferenciado IP/OOP; não há 4-bet all-in automático.
5. `G2_VS3_Benchmark_Crosscheck.csv`: análise agregada contra 15 nós públicos ART/GTO com flags `MAJOR_REVIEW`, `REVIEW` e `CROSSCHECK_ONLY`.
6. `G2_VS3_Audit_Summary.csv`: alcance e agregados condicionais; inventário de 35 nós no `G2_Nodes_Inventory.csv`.
7. Testes adicionais + preservação imutável de 8 arquivos fundamentais da v0.3.

## Validações

- `python -m unittest -q`: **114/114 OK** (v0.3 91/91 OK).
- 15×169 grid validado contra dados sintéticos; nenhuma leitura de mesa real validada.
- Nenhum código do DeepCrusher, CrusherTBP ou AoF modificado.

## Bloqueadores estratégicos

- 8 dos 15 confrontos VS_3BET mostram desvio maior que 8 p.p. em pelo menos uma ação versus comparador público. NÃO liberar nem forçar calibração apenas por percentuais agregados.
- Avaliar especialmente LJ/HJ, LJ/CO, LJ/BTN, HJ/CO, HJ/BTN, CO/BTN, BTN/SB, SB/BB.
- Rake desconhecido; stacks e sizes ainda fixos; a base VS_OPEN v0.3 também requer auditoria.
- G1 permanece ABERTO por falta de replay real de OpenHoldem 6-max.

## Próximo trabalho

1. Auditar composição de mãos por nó crítico versus premissas estratégicas; justificar cada alteração.
2. Desenvolver `VS_4BET` apenas após registrar/revisar a defesa contra 3-bet, sem marcar G2 como concluído.
3. Persistir README/changelog e hashes em toda versão; não deixar fonte de verdade esquecida.
