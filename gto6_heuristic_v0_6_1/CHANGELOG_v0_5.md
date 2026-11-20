# Changelog v0.5 — 20/11/2026

- Preservados todos os fontes Python e ranges estratégicos da v0.4 sem alterações: **não houve recalibração automática**.
- Novo `vs3_strategy_audit.py`: separa 4-bets de valor/blefe, calcula contribuição de cada classe às massas condicionais, registra fontes e estados.
- Novo `test_vs3_strategy_audit.py`: cinco testes, 119/119 total passando.
- Exportados `G2_VS3_Hand_Contributions_v0_5.csv` (2.535 linhas) e `G2_VS3_Composition_Summary_v0_5.csv` (15 linhas).
- Faixa verificada da proporção de blefes dentro das 4-bets: 6,7% a 19,3% nos ranges DRAFT; não é avaliação de EV nem prova de erro.
- Corrigido o protocolo documental G1: VS_3BET já está implementado **sinteticamente**, mas não validado com replays reais.
- Criados documentos vivos de continuidade, decisões e roadmap para a integração GitHub.
- Critério seguinte: auditar os oito nós críticos no nível das classes, não perseguir equalização numérica de benchmarks incompatíveis.
