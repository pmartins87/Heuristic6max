# MWT-3 — SRP multiway: saídas intermediárias com memória de street

**Checkpoint 20/11/2026 · DRAFT OpenPPL, sem teste no executável OpenHoldem.**

O módulo cobre a lacuna anterior de potes SRP que começam com **4–6 jogadores** no flop e passam a ter **3–5 jogadores** (2, 3 ou 4 oponentes), sem cair ainda para heads-up. A versão `multiway_v2` já possui invariantes para potes sem saídas e para transições até um único adversário, mas não contemplava os estados intermediários.

- **41 novas regras estratégicas**: 15 flop + 14 turn + 12 river. Defesas de mãos feitas e draws tornam-se mais restritas quanto mais adversários restarem; sem bluff automático em pote lotado; nuts não sofre fold por limite de preço.
- **53 topologias cronológicas novas** no universo estático delimitado, geradas por `OpponentsOnFlop`, `OpponentsOnTurn`, `OpponentsOnRiver` e `OpponentsLeft` (biblioteca OpenPPL fornecida). Esses estados são observações de quantidade de jogadores por street, **não log cronológico de bets/raises**.
- A primeira classificação de histórico por BB/limp/3bet permanece fora do domínio: só origem `f$H6CrowdedPFR` ou `f$H6CrowdedCaller`, ambas com guardas nativas de SRP, sem allin.
- Os **14 testes** verificam todas as topologias, contradições, exclusões de origem, preço, nuts, repetição de `randomhand`, integridade e ausência de regressão nas regras existentes.
- `partial_transition_policy.oppl` é a fonte das ações; `topology_helpers.oppl` é gerado por enumerador de topologia; Python apenas compõe/inspeciona esta mesma fonte.
- A camada nova não modifica um único `WHEN` anterior, não muda ranges/sizings pré-flop nem promove potes multiway 3bet/limp.

```bash
python -m unittest discover -s portability/multiway_transitions_v3 -p 'test_*.py' -q
python portability/multiway_transitions_v3/build_transitions_v3.py
git diff --exit-code -- portability/multiway_transitions_v3/topology_helpers.oppl portability/multiway_transitions_v3/preflop_multiway_partial_v3_draft.oppl portability/multiway_transitions_v3/PARTIAL_TRANSITION_TOPOLOGY.csv
(cd portability/multiway_transitions_v3 && sha256sum -c MWT3_SHA256SUMS.txt)
```

**Gate real:** identificar versão OpenHoldem; confirmar street-start counters e ação final em replay offline. Quando `OpponentsOnTurn/River` falham ou as flags mentem, o módulo pode deixar de acionar; não alegar fallback fail-closed automático. Não conectar a jogos a dinheiro real.
