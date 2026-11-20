# Roadmap vivo e gates — 2026-11-20

| Gate | Status | Próximo critério verificável |
|---|---|---|
| G0 Arquitetura | APROVADO | manter compatibilidade dos contratos |
| G1 Observação e ledger | ABERTO | replays de teste reais, comparados frame/histórico, indicadores de divergência e rejeição segura |
| G2 Pré-flop | EM AUDITORIA / HOLD | revisar matriz 15x169 VS_3BET, composições e modelo adversário, depois VS_4BET/5BET, squeeze/limps/stacks |
| G3 SRP HU pós-flop | PENDENTE | modelar linhas flop/turn/river, com SPR, iniciativa, posição e runout |
| G4 3bet/4bet/limped HU | PENDENTE | árvore própria por tipo de pote |
| G5 Multiway | PENDENTE | decisões próprias por número de jogadores |
| G6 Integração OH/OpenPPL | PENDENTE | validade de símbolos, callbacks, ações finais e rollback |
| G7 Avaliação | PENDENTE | comparação objetiva e testes de parada |

## Ordem imediata
G2-a: revisar os oito nós com discrepância agregada >8 pp. Prioridade por gravidade (`SB-BB`, `HJ-CO`, `LJ-CO`, `CO-BTN`, `HJ-BTN`, `LJ-HJ`, `BTN-SB`, `LJ-BTN`), mas confrontar cada mão e parâmetros de cenário antes de qualquer revisão quantitativa.
G2-b: construir VS_4BET com condicionamento coerente ao antecedente, depois 5-bet.
G1 paralelo: obter replays reais de teste sem apostas; não promover G1 a concluído com dados sintéticos.

## Critérios de parada
Não aprovar se faltarem: ação legal, histórico certo, range antecedente coerente, documentação de origem, dados de referência comparáveis e testes. Falha em qualquer um mantém HOLD; não declarar ganho de EV sem medição.
