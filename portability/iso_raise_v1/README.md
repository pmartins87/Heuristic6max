# ISO-1 — isolamento de limpers (DRAFT; não operacional)

**Escopo da primeira expansão (20/11/2026).** Novos contextos pré-flop separados dos ranges v0.6.1:

- CO contra 1/2 limpers; BTN contra 1/2/3 limpers, com `Raises=0`, `Calls=N`, `PotSize=1.5+N`, `StillToAct`, posição, seis jogadores e stack 95–105 BB. São **cinco contextos** novos, sem substituir RFI/VS_OPEN/VS_3BET.
- Uma **handlist nova e deliberadamente conservadora de 15 classes**, isolamento com `RaiseTo` 4.5/5.5/6.5 BB segundo número de limpers, e `Fold FORCE` residual dentro desses cinco contextos. **São heurísticas não calibradas**, NÃO charts GTO.
- Cinco marcadores `Set user_H6_ISO*` de **intenção** de raise; o pós-flop só aceita origem exclusiva, `BotRaisedBeforeFlop`, ausência de call anterior do Hero e `NumberOfRaisesBeforeFlop=0`. Isso ainda **não** certifica a ação final no OpenHoldem.
- **120 topologias** de entrada e saída de jogadores: 15 flop, 35 turn, 70 river, incluindo saídas na mesma street. A família preserva o número de oponentes no flop e limita o máximo conforme a posição/quantidade de limpers.
- **41 decisões pós-flop** autoradas na fonte OpenPPL (15 flop, 14 turn, 12 river), diferenciando HU, 2 adversários e 3+; forte proteção `HaveNuts` contra overbet, sizings e preço mais conservadores com mais oponentes. Sem bluff aleatório novo.
- `iso_policy.oppl` e `iso_preflop_capture.oppl` são a fonte das ações. `iso_interpreter.py` avalia a mesma fonte; não contém política Python separada. `build_iso.py` reconstrói o integrado a partir do pai congelado e audita a ordem de todas as regras ancestrais.

## Regressão

```bash
python -m unittest discover -s portability/iso_raise_v1 -p 'test_*.py' -q
python portability/iso_raise_v1/build_iso.py
git diff --exit-code -- portability/iso_raise_v1/iso_integrated_draft.oppl
```

São 13 testes incrementais propostos (521 execuções anteriores +13 = **534**, sujeito ao log real do CI). Não confundir execuções com testes distintos: baseline anterior 509 distintos.

## Limites e gates

1. Preflop além dos cinco casos não foi coberto: BB iso, SB iso, overlimp/coldcall/squeeze, resposta a um iso, 4bet/5bet e stacks fora de 95–105 BB permanecem pendentes.
2. `PotSize`, `Calls`, `StillToAct`, `BotRaisedBeforeFlop`, `NumberOfRaisesBeforeFlop`, reset dos `user_` e ação efetivamente executada precisam de replay **offline** do executável OpenHoldem-alvo; nenhum foi observado.
3. No-match no intérprete NÃO equivale a fallback seguro no OpenHoldem. Não utilizar o integrado em mesas reais. G1 ABERTO, G2-a HOLD para revisão dos ranges anteriores, VS_4BET bloqueado, G6 pendente.
4. Piso funcional R10d continua **não atingido**, 14/14 capacidades sem verificação completa. Esta família acrescenta cobertura, não demonstra lucratividade, EV ou excelência.

**Fonte mãe:** `portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl`. **Novo integrado DRAFT:** `iso_integrated_draft.oppl`.
