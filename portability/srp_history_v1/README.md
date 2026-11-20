# G3-HIST-v1 — árvore pós-flop dependente de históricos, SRP heads-up

**Data: 20/11/2026. Objetivo: bot heurístico COMPLETO, com muitas linhas de ação e memória contextual.** O trabalho não é um solver nem uma tese. Excelência estratégica é um **objetivo de produto**, não um resultado já comprovado. Este módulo é uma nova camada de decisões OpenPPL, não uma política Python.

## Entrega concreta

- `history_overlay.oppl` é a **fonte autoral OpenPPL** dos predicados de histórico e das decisões incrementais. Não deve ser carregado isoladamente no OH.
- `build_history.py` é um montador offline que combina o overlay com a base G3 `portability/srp_hu_mvp/srp_hu_postflop_draft.oppl` e o pré-flop existente `portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl`. Não inventa estratégia; preserva as regras ancestrais e adiciona um predicado de histórico verificável no começo de cada regra antiga de turn/river.
- `srp_hu_history_v1.oppl` é o pós-flop combinado com **14 regras flop + 16 turn + 28 river = 58 regras de ação**, além de **24 funções booleanas**, todas legíveis e autoradas em OpenPPL (inclusive 5 auxiliares preservadas da base).
- `preflop_srp_history_v1.oppl` é a versão integrada com o pré-flop existente (277 regras), em seções únicas de preflop/flop/turn/river. Não é bot operacional.
- `HISTORY_FLOP_TURN_9_PATHS.csv` é a matriz explícita de **3×3 = 9 sequências flop→turn**. O objetivo futuro é estendê-la a mais linhas de bet/raise, sizing, bordos, SPR, vilões e múltiplos adversários, sem perder o contexto prévio.
- `history_interpreter.py` lê o **mesmo OPPL** gerado, sem uma segunda política Python, permitindo simular entradas de teste. `test_history_lines.py` contém 18 testes novos, incluindo nove caminhos, preços, ambiguidade, mãos fortes, ação anterior e não regressão de pré-flop/flop. **Total do CI esperado 295 = 277 + 18.**

## Como funciona o histórico (sem inventar fatos)

Cada street anterior reconhece **três tipos específicos**:

1. **BET_CALLED (B)**: bot apostou; o adversário deu call; não houve aposta/raise do vilão, raise adversário ou call do próprio bot na street. Os flags são usados para evitar confundir com *bot raising a villain bet*.
2. **CHECKED_THROUGH (C)**: nenhuma aposta na street e nenhum raise/call do bot.
3. **CALLED_BET (X)**: bot deu call a uma aposta adversária, sem raise do próprio bot.

O river compõe nove pares BB, BC, BX, CB, CC, CX, XB, XC, XX. Cada caminho tem prioridades particulares de aposta por valor ou controle do pote com top pair/kicker bom; decisões de mãos fortes permanecem no baseline quando não houver ramo prioritário. Há um pequeno mix novo no turn, sempre usando `randomhand` nativo estável por mão.

### Qualidade e limites

- A classificação exige símbolos de histórico documentados: `BotRaisedOnFlop`, `BotCalledOnFlop`, `OpponentCalledOnFlop`, `NoBettingOnFlop`, `NoVillainBetOrRaisedOnFlop`, `NumberOfRaisesOnFlop` e equivalentes de turn. **Esses valores NÃO foram medidos no OpenHoldem-alvo.** O manual alerta que contadores dependem de leitura estável e atualização por órbita. Não afirmamos correção com scrapes perdidos.
- Linhas mais complexas (check-raise, bet-raise-call, múltiplos raises, ações conflitantes) ficam **UNCLASSIFIED**. No simulador, não há decisão de turn/river para esses casos. **No-match não equivale a fail-safe no OH**, por poder ocorrer fallback automático: não usar este arquivo com dinheiro real.
- Classificar B/C/X é somente um começo do motor de históricos. Preflop ainda pode confundir *limper + isolation raise* com SRP; o gate de identidade do pote permanece aberto.
- As ações por história são **heurísticas provisionais**. A melhoria de cobertura não prova EV, GTO nem winrate. Requer testes pragmáticos contra diferentes adversários, board texture, pot odds e bluff/value frequency antes de declarar excelência.
- Não adicionar `[WHEN Others]` genérico no lugar da lacuna de histórico. Não substituir RFI/VS_OPEN/VS_3BET históricos nem promover para G6 sem replay offline.

## Reproduzir

Na raiz do repositório:

```bash
python portability/srp_history_v1/build_history.py
python -m unittest discover -s portability/srp_history_v1 -p 'test_*.py' -q
git diff --exit-code -- portability/srp_history_v1/srp_hu_history_v1.oppl portability/srp_history_v1/preflop_srp_history_v1.oppl portability/srp_history_v1/HISTORY_FLOP_TURN_9_PATHS.csv
cd portability/srp_history_v1 && sha256sum -c HISTORY_SHA256SUMS.txt
```

## Próximos cortes, sem fase científica

**HIST-2:** guardar e distinguir mais linhas flop/turn (bet→raise, check-raise, bet-call-raise, delayed c-bet, donk), sem precisar de cada combinação aleatória de histórico inventada. **HIST-3:** interseção do histórico com classe de board (dry/wet/paired/flush/straight), posição, número de adversários, SPR, size buckets e perfil do vilão. **HIST-4:** árvore multiway, 3-bet/4-bet, limps/squeezes e estratégia de river por range; concluir a integração OH após condições mínimas de observação. O roadmap prioriza relevância estratégica e cobertura de linha, não um total de testes por si só.
