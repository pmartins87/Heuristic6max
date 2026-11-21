# P3BM-1 — potes 3-bet multiway (3–6 jogadores no flop)

**20/11/2026 · DRAFT, estratégia heurística OpenPPL, sem teste de runtime.**

- **43 novas ações**: 17 flop, 14 turn e 12 river. Os domínios incluem o Hero agressor da 3-bet (`user_H6_3betIntent`, raise efetivamente observado) ou o Hero que abriu, enfrentou a 3-bet e pagou (`user_H6_RFIIntent`, raise e call observados). Uma mão que não possui a origem correta **não é promovida**.
- O `NumberOfRaisesBeforeFlop = 1` representa um raise **adversário** na biblioteca OpenPPL, nunca `2` por contar erroneamente o raise do Hero. Isso exclui 4-bets/5-bets adversárias do módulo.
- **117 topologias** estáticas de flop/turn/river para 2–5 oponentes no flop, que podem diminuir até um único adversário. A matriz tem 234 linhas incluindo os dois papéis do Hero.
- Defesas e value variam pelo número de oponentes restantes, não fazem c-bet automática de air em potes 3-bet multiway; prioridade explícita de nuts frente a qualquer overbet, evitando `Fold FORCE` por preço.
- **12 testes** de origem, cronologia, prioridade, contagem, regressão do ancestral, exclusão de SRP/limp/4bet e recomposição exata do OpenPPL.
- Nenhuma alteração nos ranges RFI/VS_OPEN/VS_3BET nem nas decisões pré-flop. A integração atual é `preflop_srp_limp_3bet_multiway_draft.oppl`.

```bash
python -m unittest discover -s portability/p3bet_multiway_v1 -p 'test_*.py' -q
python portability/p3bet_multiway_v1/build_3bet_multiway.py
git diff --exit-code -- portability/p3bet_multiway_v1/threebet_multiway_topology.oppl portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl portability/p3bet_multiway_v1/THREEBET_MW_TOPOLOGY.csv
(cd portability/p3bet_multiway_v1 && sha256sum -c P3BM1_SHA256SUMS.txt)
```

**Limite central:** valores observados no próprio OpenHoldem e comportamento real de `Set user`/ações finais NÃO foram medidos. Declarações de excelência estratégica ou piso de completude R10d **continuam bloqueadas**. Não usar para apostas reais.
