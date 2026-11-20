# G1 — Protocolo de evidência real (ainda não executado)

Esta versão possui testes de histórico **sintéticos**. Ainda não valida os outputs do OpenHoldem em uma mesa 6-max real. A próxima etapa deve coletar amostras do ambiente de **teste**, sem apostas de dinheiro real e sem comportamento de autoplayer.

## Mínimo de evidência por mão

- Hand ID, jogo 6-max cash, evento de início/fim e blinds.
- Posições mapeadas: LJ/HJ/CO/BTN/SB/BB; IDs consistentes durante a mão.
- Stacks iniciais e os valores por street, sem normalizar silenciosamente fichas incorretas.
- Sequência de ações com ator, tipo, alvo de raise e registro observável antes/depois.
- Pote e currentbet em dois snapshots estáveis, sem usar frames transitórios como ações.
- Resultado auditado de 3bet/limp/fold e data quality; ação incerta => rejeitar.

## Matriz mínima de replay

1. RFI limpo nas 5 posições e VS_OPEN nos 15 pares.
2. BB vs SB RFI 3 BB: pote total 4 BB.
3. BTN open 2.5 BB: BB defende, SB folda.
4. Open -> cold call -> atuação do BB: não é VS_OPEN puro.
5. Limp -> ISO -> Hero: não é VS_OPEN puro.
6. Open -> 3bet -> Hero: VS_3BET implementado no modelo sintético v0.4, mas ainda não validado com replay real.
7. Full raise, shove parcial, shove não reabrindo ação; rejeição do erro antes de alterar saldos.
8. Frame inválido, desconexão, leitura inconsistente de `currentbet`, cards ilegíveis, chair trocado, mão duplicada.

## Gate

O gate G1 só poderá ser aprovado quando os sinais de OpenHoldem e o histórico reconstruído forem comparados mão a mão, com indicadores de erro, tolerâncias e casos inconclusivos registrados. O JSON canônico por si só não atende a esse requisito.
