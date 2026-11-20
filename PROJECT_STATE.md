# Estado atual — Heuristic6max

**Data:** 20/11/2026 | **Versão:** v0.5 (auditoria) | **Estado:** HOLD / não operacional.

## O que está concluído
- G0: arquitetura e contratos de estado; base aprovada.
- G1: máquina de histórico e observações em teste **sintético**; replays reais continuam pendentes.
- G2 parcial: RFI 5×169 (845 registros), VS_OPEN 15×169 (2.535), VS_3BET 15×169 (2.535). Todas são hipóteses DRAFT, não soluções GTO.
- VS_3BET: 888 classes alcançáveis a partir do RFI e 1.647 não alcançáveis.
- v0.4: 114 testes. v0.5: auditoria de composição por mão, **119 testes locais aprovados**. v0.5 não altera ação estratégica v0.4.

## Hipóteses restritas
Cash NLHE 6-max, 100 BB alvo (95–105), SB 0,5 e BB 1, sem ante; RFI 2,5 BB LJ–BTN / SB 3 BB; 3bet em sizing pré-estabelecido, sem limper/caller/squeeze/short stack. Rake não calibrado. Sem política pós-flop, 4bet/5bet ou integração OH operacional.

## Descobertas e limites
- Benchmark agregado v0.4: 8/15 nós divergiram >8 p.p., 4 divergiram 4–8 p.p., 3 divergiram até 4 p.p.; **rake e árvore diferem**, logo não é prova de EV.
- v0.5: blefes representam entre 6,7% e 19,3% da massa de 4-bets dos ranges DRAFT; não é frequência ótima.
- Não há medição de winrate, EV, solver equivalência nem replay real de OpenHoldem.

## Integridade da fonte
A v0.5 completa foi gerada localmente em `GTO_Heuristic_6Max_v0.5_Auditoria_Composicao_Handoff.zip` com fontes Python, CSV, docs e SHA256. **Enquanto esse pacote não estiver integralmente replicado no GitHub, a continuidade apenas pelo repositório é incompleta.** Não recriar código ausente a partir de descrições nem afirmar que está versionado.

**Próxima decisão:** auditar as classes dos oito `MAJOR_REVIEW` antes de mudar frequências ou iniciar VS_4BET. **Ação para o usuário:** subir o conteúdo extraído do ZIP v0.5 ao GitHub, preservando estes documentos, para continuidade independente do chat.