# Nota de decisão G2-a / v0.7

- **Decisão adotada:** evidência de risco condicional de subdefesa; priorizar revisão de CALL+4BET contra 3bet, NÃO alterar ranges, NÃO iniciar VS_4BET.
- **Justificativa:** a v0.6.1 calibrava agregados; a nova métrica com combinação física adversária revela defesa insuficiente para manter um blefe isolado de equidade nula não lucrativo em sete dos oito nós críticos (um marginal), mas não representa o jogo completo.
- **Mudaria se:** rake, sizings, risco de cold-4bet dos jogadores restantes ou rangearia adversária invalidarem a hipótese. Com rake alto e calls desfavoráveis, concessão de fold pode ser racional.
- **Gates:** G2-a HOLD, G1 aberto, G2-b bloqueado. v0.6.1 intocado. Arquivos source e CSV do audit devem ser mantidos no GitHub.
