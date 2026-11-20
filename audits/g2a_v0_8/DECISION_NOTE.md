# Nota de decisão ADR-012 — auditoria v0.8

- **Nova evidência:** 15/15 distribuições pós-RFI+3bet reconstruídas por classe física; HJ-CO concentra 58,1119 pp dos folds em quatro famílias, especialmente 23,2205 pp de suited-outros e 11,2818 pp de pocket pairs 22–66, todas FOLD puro. Variação de cold actions desmonta a interpretação forte de sete alarmes v0.7 como exploração comprovada.
- **Decisão:** revisão conjunta de seleção RFI e defesa VS_3BET, sem declarar FOLD errado nem aumentar calls ou 4bets automaticamente.
- **Preservar:** v0.6.1 e v0.7, inclusive CSVs e decisões; G1 aberto; G2-a HOLD; G2-b bloqueado. DeepCrusher/CrusherTBP intocados.
- **Mudaria com:** premissas de rake/cap e sizing da plataforma-alvo + análise de equidade/realização por classes + replays de teste, justificando mudança **por mão** e prova de regressão, não pela comparação de percentuais agregados.
- **Escopo da v0.8:** relatórios, teste e diagnóstico; não produz um bot jogável nem EV real.
