# MLIMP-2 — BB contra 2–5 limpers e histórico multiway

**20/11/2026 · DRAFT OpenPPL.** Expande o módulo anterior de BB contra **um** limper sem apagar seu comportamento.

- Pré-flop: **7 contextos** exclusivos de opção de CHECK do BB: dois a quatro limpers com/sem SB completando (6 contextos) e cinco limpers incluindo SB (1). `PotSize` distingue se o SB contribuiu apenas com o blind inicial ou completou; não inferir a origem sem essa guarda.
- Cada novo ramo grava `user_H6_ML{n}{SB|Other}` via `Set` e emite `Check FORCE`. O pós-flop verifica `BotCheckedPreflop` **realmente observado**, `BotRaisedBeforeFlop = false`, `BotCalledBeforeFlop = false`, zero raises adversários e ausência de flags incompatíveis.
- Pós-flop: **39 novas regras** (14 flop, 13 turn, 12 river) para potes que começaram com 2–5 limpers, sejam ainda multiway ou tenham se tornado HU. As decisões variam pela quantidade atual de oponentes; nuts não sofre fold em overbets, mãos marginais são defendidas com maior seletividade em potes lotados.
- **117 topologias cronológicas teóricas** por street e número de oponentes (179 linhas incluindo origens SB/Other), com `OpponentsOnTurn` e `OpponentsOnRiver` monotônicos.
- **12 novos testes** percorrem contextos, exclusões, reavaliação, preservação e reprodutibilidade. Python interpreta a mesma fonte `.oppl` e não é a política de runtime.

```bash
python -m unittest discover -s portability/multilimp_bb_v2 -p 'test_*.py' -q
python portability/multilimp_bb_v2/build_multilimp.py
git diff --exit-code -- portability/multilimp_bb_v2/multilimp_topology.oppl portability/multilimp_bb_v2/multilimp_preflop_capture.oppl portability/multilimp_bb_v2/preflop_multiway_partial_multilimp_v2_draft.oppl portability/multilimp_bb_v2/MULTILIMP_TOPOLOGY.csv
(cd portability/multilimp_bb_v2 && sha256sum -c MLIMP2_SHA256SUMS.txt)
```

**Fora do escopo:** isolamento (iso-raise), limp/call, limp/3bet, short stacks e comportamento real de `BotCheckedPreflop` não validado no OpenHoldem-alvo. Sem garantia fail-closed de no-match ou lucro; não executar em mesas reais.
