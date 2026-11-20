# v0.6 — G2-a card-removal-conditioned audit | 20/11/2026

- Preservados integralmente os 51 arquivos-base da v0.5 e seus 119 testes (nenhum range, decisão ou router foi alterado).
- Novo `vs3_blocker_audit_v0_6.py`: enumeração das 1.326 combinações físicas para condicionar `P(4bet/call/fold)` à 3-bet do modelo VS_OPEN, considerando bloqueio de cartas.
- Novo `test_vs3_blocker_audit_v0_6.py`: 5 testes, incluindo conferência independente por força bruta para três confrontos e quatro combinações físicas.
- Total: **124 testes locais aprovados**, sem replay real/EV/solver.
- Novos CSVs para 15 confrontos, contribuições por mão e 8 flags de benchmark; limites detalhados em `G2A_METHOD_AND_FINDINGS_v0_6.md`.
- G1 aberto, G2-a HOLD, G2-b VS_4BET bloqueado até revisão estratégica comparável.
