# BLISO-2 — isolamento de limpers pelo SB/BB (DRAFT, não operacional)

**Objetivo:** preencher o espaço após ISO-1 sem revisar automaticamente RFI, VS_OPEN, VS_3BET ou o próprio ISO-1. A política de decisão continua exclusivamente no código OpenPPL.

## 13 origens novas e exclusivas

- **SB contra 1–4 limpers:** quatro contextos, `StillToAct=1`, `AmountToCall=0.5 BB`, pote `1.5+Calls`, `RaiseTo` entre 4.5 e 7.5 BB com mão da handlist específica; demais mãos recebem `Fold FORCE` no domínio estrito novo.
- **BB contra 1–5 limpers:** nove contextos, `StillToAct=0`, `AmountToCall=0`. Distinguir SB completado (`PotSize = 1+Calls`) de SB não completado (`PotSize = 1.5+Calls`, apenas até quatro limpers). `RaiseTo` entre 4 e 8 BB para a lista específica; **sem fold** para os demais: permanecem sujeitos ao Check anterior, preservando o histórico de limp BB.
- 13 novos `Set user_H6_BISO*` são marcadores de **intenção** de raise, nunca provas de clique executado. Um estado pós-flop requer um único tag novo, nenhum dos 5 tags ISO-1, nenhum tag RFI/3bet/limp BB, `BotRaisedBeforeFlop`, `NOT BotCalledBeforeFlop`, `NOT BotCheckedPreflop` e `NumberOfRaisesBeforeFlop=0`.
- Handlist **separada** de 15 classes (ainda heurística não calibrada); os antecessores permanecem intactos.

## Pós-flop e geometria

A fonte `blind_iso_policy.oppl` tem **43 regras** (16 flop, 14 turn, 13 river). A árvore herda a topologia cronológica de ISO-1 (120 combinações por street) por adaptação da **fonte OpenPPL já autorada**: contar oponentes no flop, turn e river, inclusive quedas durante uma street. Máximo de oponentes no flop = número de limpers +1 para Hero SB (BB ainda por agir) ou número de limpers para Hero BB.

- 1 adversário, 2 adversários e 3+ recebem limites distintos de preço; a origem SB versus BB também diferencia aposta de valor heads-up.
- `HaveNuts` é defendido contra overbet sem cair no fold genérico; sem novos blefes automáticos.
- **Não é solver nem prova de EV**; são heurísticas submetidas a revisão futura de board, SPR, rake e sizings.

## Reproduzir

```bash
python -m unittest discover -s portability/blind_iso_v2 -p 'test_*.py' -q
python portability/blind_iso_v2/build_blind_iso.py
git diff --exit-code -- portability/blind_iso_v2/blind_iso_integrated_draft.oppl
(cd portability/blind_iso_v2 && sha256sum -c BLISO2_SHA256SUMS.txt)
```

São **18 novos testes aprovados** no [workflow 44858080418](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418). O log executou 28 suítes e 552 testes; descontando 12 execuções duplicadas do R10d, são **540 testes deduplicados por suíte**.

## Gates e limitações

As condições sobre `Calls`, `PotSize`, `BotRaisedBeforeFlop`, `BotCheckedPreflop`, memórias `user_` e o `RaiseTo` exato ainda **não foram verificadas no OpenHoldem real**. O isolamento BB versus single-limp e suas condições de SB completado são modelos estáticos, não capturas de execução.

Sem resposta contra iso, coldcall/squeeze, short/deep, 4bet/5bet e histórico de ações real. No-match do intérprete Python não significa fail-closed no OpenHoldem. **Não carregar o DRAFT para apostas reais.** G1 e G6 pendentes; G2-a HOLD; meta 14/14 R10d não aprovada.

Parent: `portability/iso_raise_v1/iso_integrated_draft.oppl`. Novo candidato: `blind_iso_integrated_draft.oppl`.
