# Roadmap vivo — 20/11/2026 (v0.6.1)

| Gate | Estado | Critério de avanço |
|---|---|---|
| G0 Arquitetura | APROVADO | contratos mantidos |
| G1 Histórico/observação | ABERTO | replays reais de teste, divergências e fallback seguro |
| G2-a Pré-flop RFI / VS_OPEN / VS_3BET | HOLD | revisar mãos e contabilidade do jogo; conferir compatibilidade de premissas; documentar decisão |
| G2-b VS_4BET/5BET, squeeze, limps, outros stacks | BLOQUEADO | liberar G2-a primeiro |
| G3 Pós-flop SRP HU | PENDENTE | flop/turn/river por nó e histórico |
| G4 Pós-flop 3bet/4bet/limped HU | PENDENTE | árvores específicas |
| G5 Multiway | PENDENTE | ranges e nós multiway distintos |
| G6 Integração OpenPPL/OpenHoldem | PENDENTE | replay + ação final + rollback |
| G7 Avaliação | PENDENTE | benchmarks comparáveis, EV/risco e critérios de parada |

## Feito nesta rodada
- A fonte completa v0.5 foi publicada no GitHub.
- v0.6 republica snapshot autocontido (61 arquivos), adiciona cálculo com card removal e cinco testes; 124 testes passaram.
- Auditoria condicional de 15 nós e tabela de 8 MAJOR_REVIEW publicada; decisões estratégicas **não alteradas**.
- **v0.6.1 integridade:** 50/50 arquivos-base de conteúdo preservados; manifesto regenerado, errata e verificador/CI corrigidos. Sem mudança estratégica.

## Próxima decisão concreta
Revisar os oito nós (SB–BB, HJ–CO, LJ–CO, CO–BTN, HJ–BTN, LJ–HJ, BTN–SB, LJ–BTN) por mão e por premissa de 3-bet de vilão. Primeiro definir modelo econômico alvo (rake, cap, sizings). Distinguir evidência válida de simples diferença numérica frente a tabelas externas.

**Critérios de parada:** não aprovar range por acertar frequência agregada, não passar ao VS_4BET com antecedente não auditado, não validar G1 por replay sintético, não marcar pronto sem rota de ações legais e sem avaliação de qualidade.
