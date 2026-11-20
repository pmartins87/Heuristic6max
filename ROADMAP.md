# Roadmap vivo e gates — 20/11/2026

| Gate | Estado | Critério verificável |
|---|---|---|
| G0 Arquitetura | Aprovado | preservar contratos |
| G1 Observação e ledger | Aberto | replays reais de teste auditados, divergências quantificadas, rejeição segura |
| G2 Pré-flop | Parcial / HOLD | auditar RFI/VS_OPEN/VS_3BET, depois VS_4BET/5BET, squeeze, limps, diversos stacks e rake |
| G3 Pós-flop SRP HU | Pendente | árvores flop/turn/river contextualizadas |
| G4 3bet/4bet/limped HU | Pendente | árvores distintas para cada classe de pote |
| G5 Multiway | Pendente | decisões específicas para vários participantes |
| G6 OpenPPL/OH | Pendente | integração, símbolos, ação final, replay e rollback |
| G7 Avaliação | Pendente | EV/benchmarks comparáveis, regressões e stop rules |

## Prioridade imediata
**G2-a:** auditar oito nós com disparidade agregada >8 p.p.: SB-BB, HJ-CO, LJ-CO, CO-BTN, HJ-BTN, LJ-HJ, BTN-SB, LJ-BTN. Examinar as mãos, a faixa de 3bet adversária, blockers, rake, sizing e ancestral RFI; NÃO forçar coincidência dos percentuais.
**G2-b:** só após concluir G2-a, iniciar VS_4BET com antecedente coerente.
**G1 paralelo:** coletar replays reais *de teste sem apostas*; não chamar G1 concluído por testes sintéticos.

## Gates de parada
Nenhum cenário é aprovado sem histórico consistente, ação legal, range ancestral coerente, fonte de confiança identificada, replay representativo e avaliação estratégica coerente. `None` não é Fold/Check. Se faltar fonte ou evidência, manter HOLD.