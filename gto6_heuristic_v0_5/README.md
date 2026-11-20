# GTO Heuristic 6-Max — v0.5 (AUDITORIA / HOLD)

**Projeto:** desenvolvimento incremental de estratégia heurística para cash NLHE 6-max, buscando princípios GTO sem solver de equilíbrio. **Não há estratégia operacional aprovada.** Ranges DRAFT não podem ser usados em mesas; retornos `None` indicam falta de cobertura.

**Fonte de verdade:** https://github.com/pmartins87/Heuristic6max — reler e atualizar documentação viva a cada revisão. Leia também `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md` e `CHANGELOG.md`.

## Estado
- G0 aprovado; G1 aberto (apenas replays sintéticos); G2 parcial/em auditoria; G3–G7 pendentes.
- v0.4 possuía RFI 5x169, VS_OPEN 15x169, VS_3BET 15x169 e 114 testes.
- v0.5 mantém todas as decisões da v0.4, acrescentando decomposição da massa de 4-bets por mão e 5 testes (119/119).
- Sem comparação de EV, sem prova de proximidade GTO e sem integração OpenHoldem validada.

## Descoberta da auditoria
A parcela de 4-bet blefe dentro das 4-bets geradas é de 6,7–19,3% dependendo do confronto (estatística interna de v0.4, NÃO benchmark GTO). Oito nós têm divergência agregada >8 pontos percentuais contra referência externa não equivalente em rake/árvore. Portanto, status HOLD, não aprovação.

## Reproduzir
Python 3.10+ com biblioteca padrão:
```sh
python -m unittest -q
python vs3_strategy_audit.py
```

## Integridade e entrega
O pacote v0.5 com todos os arquivos precisa ficar versionado junto da documentação, não apenas em uma conversa. Conferir `SHA256SUMS.txt`. Não modificar arquivos originais de DeepCrusher/CrusherTBP/AoF.

## GitHub — acompanhamento da importação
- [Issue #1 — Importação do código completo](https://github.com/pmartins87/Heuristic6max/issues/1) (bloqueador de autonomia de outros chats/IA).
- [Issue #2 — Auditoria por mão dos 8 nós críticos](https://github.com/pmartins87/Heuristic6max/issues/2).
- O repositório já contém os documentos e alguns relatórios, **mas, no momento desta entrega, o código integral v0.5 ainda precisa ser enviado ao GitHub**.
