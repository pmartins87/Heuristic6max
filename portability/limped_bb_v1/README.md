# LIMP-BB-v1 — resposta ao limp isolado com check de BB e pós-flop próprio

**Heuristic6max, 20/11/2026 — DRAFT sem OpenHoldem executado.** Mais um módulo rumo à abrangência superior ao DeepCrusher_R10d, não um bot operacional. Não altera nenhuma política anterior de RFI, VS_OPEN, VS_3BET ou pós-flop.

## Escopo efetivamente implementado

- No pré-flop 6-max, se BB chega à opção após **exatamente um limp adversário**, nenhum raise, `AmountToCall=0`, `StillToAct=0`, stacks conhecidos 95–105 BB e pote compatível, `Check FORCE` e captura de intenção.
- Dois tipos de origem: limp do **SB** (pote de 2 BB; BB está IP) e limp de **outra posição com SB fold** (pote de 2,5 BB; BB está OOP). São hipóteses de reconstrução que precisam de replay para confirmação.
- `limp_bb_postflop.oppl`: **33 regras** (13 flop + 11 turn + 9 river), fontes OpenPPL de value, draws, price, seletividade posicional e proteção contra fold com nuts. A mistura de aposta seletiva usa `randomhand`, fixo na mão.
- `limp_bb_preflop_capture.oppl`: duas regras de `Set user_...` e duas de `Check FORCE`, geradas deterministicamente. São apenas marcadores de **intenção**. No pós-flop, os predicados exigem também o símbolo nativo **`BotCheckedPreflop`** (grafia confirmada no `OpenPPL_Library_Integrated.txt`), nenhuma ação de raise/call do bot e nenhum raise dos adversários.
- `preflop_multiway_limp_bb_draft.oppl`: fonte integrada preservando a ordem e o conteúdo literal de todos os `WHEN` anteriores. O `build_limp_bb.py` gera essa fonte. `limp_source_interpreter.py` lê **a própria** fonte OpenPPL para os **17 testes** de regressão.

## Não confundir com limp/iso completo

Não cobre múltiplos limpers, SB limp e BB isolando com raise, Hero que dá limp/call de outra posição, limp/3bet, limp multiway, straddles, short stacks, nem potes com adversários que abandonaram a mão depois do flop. O símbolo `BotCheckedPreflop` reflete o histórico interno do autoplayer e não pode ser presumido verdadeiro antes de observar a versão real do OpenHoldem. O `default.bot` pode agir em estados sem regra. **M04 (Limped/Isolation) permanece PARTIAL**, nunca VERIFIED.

A heurística atual é aproximada, não demonstra GTO nem superioridade em winrate. Ela aumenta cobertura de decisões, mas não satisfaz sozinha o gate obrigatório R10d.

## Testes

```sh
python -m unittest discover -s portability/limped_bb_v1 -p 'test_*.py' -q
python portability/limped_bb_v1/build_limp_bb.py
git diff --exit-code -- portability/limped_bb_v1/limp_bb_preflop_capture.oppl portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl
(cd portability/limped_bb_v1 && sha256sum -c LIMP_BB_SHA256SUMS.txt)
```

**Prioridade seguinte:** desenvolver limp/iso real (inclusive BB isolation e SB limp/call), múltiplos limpers, além de árvore completa VS_4BET e squeeze, sujeitos a estados de histórico observáveis e regressão. Não chamar a fonte DRAFT de perfil seguro antes da execução offline no OpenHoldem.
