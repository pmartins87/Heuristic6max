# Postflop 3bet-pot heads-up — entrega OpenPPL DRAFT

**20/11/2026 — 41 regras novas de decisão flop/turn/river, 4 helpers, 2 estados de origem pré-flop.** O módulo preserva os ranges e a ação preflop do `srp_history_v3/` exatamente como estavam. Não é validação OpenHoldem, nem estratégia GTO resolvida.

## O que realmente mudou

- `threebet_hu_postflop.oppl`: regras nativas com prioridade primeiro valor/continuação e depois proteção contra bets, draws, mixes e checks. **16 flop + 14 turn + 11 river = 41 ações DRAFT.** Não há política multiway/4bet neste arquivo.
- `preflop_intent_capture.oppl`: **9 condições de intenção RFI e 44 VS_OPEN 3bet** são geradas das mesmas regras `RaiseTo` pré-existentes. Executam `Set user_H6_RFIIntent` ou `Set user_H6_3betIntent` antes das ações originais, mantendo todas as ações de pré-flop.
- `preflop_srp_and_3bet_hu_draft.oppl`: combinado único OpenPPL, com os dois estados de origem, 4 helpers de identificação de potes e 41 ações novas em cada street *antes* das regras SRP. Os domínios evitam competição: SRP tem NumberOfRaisesBeforeFlop = 0 ou call sem raise do bot, enquanto 3bet do Hero requer 1 raise adversário e origem de 3bet; caller da 3bet exige origem RFI + raise/call realizado.
- `p3bet_interpreter.py` interpreta diretamente o `.oppl` de 3bet para testes, sem nova estratégia paralela em Python; `test_p3bet_hu.py` tem 15 testes. `build_p3bet_hu.py` gera todos os trechos e compara contagens de intenções. O mapeamento final é fonte única.

## Limites que NÃO podem ser ocultados

Os novos marcadores `Set user_...` capturam **intenção** de RaiseTo, não a execução efetiva. O roteamento pós-flop **também exige** `BotRaisedBeforeFlop`, `BotCalledBeforeFlop`, contagem de raises e um único adversário desde o flop. Isso reduz falso positivo, mas não valida o significado do histórico no OpenHoldem-alvo, nem prova ausência de ação ilegal/fallback. Um reset da mão pode apagar os marcadores. O plano precisa comparar a ação real em replay offline.

O módulo ainda não classifica potes 4bet, 5bet, limped/iso, squeeze, multiway e all-in. Ao faltar evidência, a fonte **não emite ação** para eles — o OpenHoldem pode ter fallback próprio, portanto este arquivo **NÃO deve operar em mesas reais**. R10d continua substancialmente mais abrangente nesta etapa; consulte [benchmark mínimo](../../benchmarks/r10d_floor/README.md).

Ações `BetHalfPot`, `BetTwoThirdPot`, `BetThirdPot`, `RaiseHalfPot` e `randomhand` constam no manual histórico. As condições exatas de valor e draw **são heurísticas novas**, não tabelas derivadas de solver; devem ser refinadas por contexto de posição, runout, SPR, call price e oponente nas próximas versões.

## Reproduzir

```sh
python -m unittest discover -s portability/p3bet_hu_v1 -p 'test_*.py' -q
python portability/p3bet_hu_v1/build_p3bet_hu.py
git diff --exit-code -- portability/p3bet_hu_v1/preflop_intent_capture.oppl portability/p3bet_hu_v1/preflop_srp_and_3bet_hu_draft.oppl
(cd portability/p3bet_hu_v1 && sha256sum -c P3BET_HU_SHA256SUMS.txt)
```

**Próximo ganho com impacto:** escopo confiável do pote/observação, potes 3bet com 3 players, multiway SRP e limped/iso; depois game families 4+ e pós-flop short-stack, sem mais loops de testes supérfluos. Eficácia estratégica só poderá ser avaliada em ambiente controlado e com observação da ação final.

## Correção de proteção ao nuts (hotfix da mesma linhagem)
No flop/turn, após a possibilidade de RaiseHalfPot, uma mão `HaveNuts` agora recebe **Call sem limite artificial de 100%/85% PotSize**. Antes, uma overbet muito grande escapava ao call genérico e era direcionada erroneamente ao fold. Testes incluem 250% do pote. Essa correção muda as novas heurísticas DRAFT, **não** os ranges pré-flop.
