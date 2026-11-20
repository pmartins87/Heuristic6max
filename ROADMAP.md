# Roadmap vivo — 20/11/2026 (auditoria v0.11 de fontes / estratégia v0.6.1)

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

## Evidência e prioridade acrescentadas pela v0.7
- Publicada auditoria matemática por 1.326 combos físicos do adversário, fold condicional por mão e preço exato da 3bet: [audits/g2a_v0_7/](audits/g2a_v0_7/).
- **7/8 nós** exibem *pressão condicional positiva* no experimento isolado de equidade zero; BTN-SB é limítrofe. Não confundir com exploração real no jogo completo.
- Revisar **defesa combinada (4bet+call) e fold vs preço**, priorizando HJ-CO, HJ-BTN, LJ-HJ, LJ-CO, LJ-BTN, CO-BTN. Testar alternativas condicionais a rake/cap e sizing antes de alterar ranges. Nenhuma mudança G2-b autorizada.

## Atualização G2-a / v0.8
- Auditoria de 169 classes com posterior por RFI+3bet e card removal; quatro CSVs, 11 testes adicionais.
- Falhas de defesa devem ser investigadas em **conjunto com o ancestral RFI**, não resolvidas transferindo mãos para CALL indiscriminadamente.
- Novo gate de revisão por mão: documentar premissa de rake/cap/sizing e matriz de EV (call, fold, 4bet) sob modelo explícito do adversário, com incerteza; só então mudar frequências individuais.
- Variações de cold action demonstram fragilidade do contrafactual v0.7 em nós com jogadores atrás; sem alegar subdefesa GTO comprovada.
- G1 real-replay ainda aberto; G2-a HOLD; G2-b (VS_4BET) bloqueado.

## G2-a / v0.9 — faixa de análise econômica HJ–CO
- Nova medição rastreável: 169 classes, 15 candidatas, 36 fronteiras hipotéticas para 3bet 8/9,5/11 BB, rake artificial e fatores de realização 60–100%; 11 testes novos.
- **Não** comparar apenas frequência de fold; uma poda de RFI pode baixar o fold condicional e **piorar EV de open**. Converter fold em call exige equity/realização; 4bet exige modelo explícito de desistência/continuação.
- Próximo gate: obter premissas operacionais de rake/cap/sizings e estimar equity contra range de 3bet do modelo por mão com método verificável. Depois comparar EV de OPEN vs FOLD inicial e CALL/4BET vs FOLD frente a 3bet, sem ajustes até validação.
- Estado inalterado: G1 aberto, G2-a HOLD, G2-b bloqueado, G3–G7 pendentes.

## Auditoria v0.10 — HJ/CO equities, sem mudança estratégica
- [Método e referência v0.10](audits/g2a_v0_10/README.md), [169 equities por classe](audits/g2a_v0_10/HJ_CO_EQUITY_169_REFERENCE_v0_10.csv), [15 conferências Monte Carlo](audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv).
- A fonte privada fornecida tinha 1.624.350 confrontos físicos ordenados, cobertura/reciprocidade conferidas; licença/autoria não documentadas, portanto **não publicar o bruto**. SHA-256 da fonte e método presentes no README da auditoria. Motor MC em Python stdlib pode reestimar sem a fonte original.
- Ex.: AQo 41,3101%, AJo 35,6951%, KJo 32,3099%, TT 44,0217% de **equidade bruta de showdown** contra a política 3bet do CO. Isso NÃO determina EV de call fora de posição, nem prova que folds existentes estão errados.
- 10 testes novos; total acumulado previsto **163 (124+7+11+11+10)**. Todos os ranges e o snapshot v0.6.1 permanecem intactos; G1 aberto, G2-a HOLD, G2-b bloqueado.

**Próximo gate:** comparar equidade *realizada* e custo/rake da plataforma em cenários HJ OOP, inclusive possíveis ações de jogadores restantes, antes de alterar qualquer mão. Não confundir showdown equity e call EV.

## G2-a / v0.11 — validação de referências e parada de compute especulativo
- [Gate de fontes](audits/g2a_v0_11/README.md): três fornecedores analisados, nenhum verificado como substituição exata para HJ/CO (100 BB, open 2,5 BB, 3bet 8 BB, rake/cap não documentados).
- Mantidas a arquitetura e a estratégia Python v0.6.1; nenhuma transcrição OpenPPL antecipada.
- **Parada técnica:** novas auditorias ilustrativas de EV/EQR só com novas evidências que possam alterar a conclusão; priorizar rake/cap e sizings do ambiente-alvo, correspondência da chart e/ou replays reais de G1.
- G2-a continua HOLD, G2-b continua BLOQUEADO, G6 é FUTURO.


## Gate transversal PORT-0 a PORT-3 (ADR-016)
- PORT-0: contrato publicado; 2 regras puras BTN RFI em texto OpenPPL; intérprete Python lê as mesmas linhas; 7 testes estáticos / 3.042 estados.
- PORT-1: antes de desenvolver novas regras executáveis, validar predicados/símbolos, prioridade top-down, RaiseTo/By, unidades, histórico, scrape, legalidade e ausência de correspondência. Não aceitar fonte Python-only como ação exportável.
- PORT-2: bloqueado para mixes até verificação de aleatoriedade estável e memória; SHA256 Python difere de Random OPPL.
- PORT-3 (G6): exigir teste com OpenHoldem alvo em replays sem apostas, conferindo ação final e fallback. G1/G2 mantêm seus gates anteriores.
Ver [PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md).

## PORT-1 parcial — árvore de RFI LJ
- Representar apenas o subdomínio de 168 mãos puras da LJ, com guardas de seis jogadores, stacks, posição, pot e RFI, usando texto OpenPPL. KJo (40% raise) NÃO pode ser arredondado.
- **Próximo gate:** provar mistura estável do KJo; validar todos os símbolos, NoMatch/fallback e ação final na versão instalada de OH por replays sem apostas. Sem isso PORT-1 não está aprovado e G6 não é liberado.
- 15 testes novos. Não alterar G2-a HOLD, ranges v0.6.1, G1 ou G6.

## PORT-2 — atualização transversal de portabilidade
- **Novo dado técnico:** OpenPPL/OH documenta `randomhand` em [0,1), fixo por mão. KJo 40/60 da LJ agora tem 2 regras explícitas complementares no mesmo arquivo OpenPPL; 19 novos testes estáticos.
- **PORT-1/2 estático:** a lacuna de expressabilidade da mistura KJo foi eliminada; o gate operacional continua aberto. Não alterar gates G1, G2-a, G2-b, G6 nem os 3 ranges.
- **Próximo gate mensurável:** OH-alvo instalado e versão identificada → replays sem dinheiro → confirmar amostras de `randomhand`, estabilidade por mão, 0.40, escopo correto da posição/stack, sizing final `RaiseTo`, e comportamento de no-match/fallback. Sem esses resultados, não autorizar exportação operacional.

## PORT-3 / RPL-0 — gate de replay preparado, não validado
- Auditor de evidência reproduzível implementado com 27 testes, mais 6 fixtures explícitas e relatório de 5 casos STATIC_ONLY + 1 BLOCKED_NO_MATCH.
- **Aceitação do próximo gate PORT-3b:** OH-alvo/build identificado; ManualMode ou OHReplay desconectados de mesa real; `f$debug` registrando os símbolos; ações `Best action` e `Action taken` (e sizing) obtidas de **mesma mão**, evidência local com hash; estabilidade de `randomhand` e sem fallback silencioso. Uma passagem parcial não é aprovação.
- **Parada atual:** sem arquivo de replay real, parar a inferência de runtime. Preservar PORT-1/PORT-2, G1 ABERTO, G2-a HOLD, G2-b BLOQUEADO, G6 PENDENTE; não mudar a estratégia.
