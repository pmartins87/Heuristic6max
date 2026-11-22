> **ROADMAP V2 — ADR-049:** [Plano](v2/PLAN.md). Priorizar **famílias estratégicas por risco, impacto e abrangência**, não percentuais exatos, dois flops ou full house. [Defesa/agressão em todas as streets](v2/families/DEFENDING_VS_AGGRESSION_F1.md) é primeiro F1 transversal; [16 mecanismos R10d triados](v2/DEEPCRUSHER_TRANSFER_AUDIT.md). A trilha F1/F2 evolui sem depender da instalação local do OH; a trilha F3/F4 permanece OH_PENDING para certificação. F5 BLOCKED; 0 módulos completos certificados. Abaixo: histórico do roadmap anterior.

> **ROADMAP V2 ATUAL — ADR-048:** [Plano Vivo](v2/PLAN.md). F0 PASS_CONCEPTUAL; F1 piloto BTN 2,5BB/100BB PASS_PILOT_CONTEXT; F2 OPEN com 2 decisões de c-bet revisadas; F3 **STATIC_SYMBOLIC_VERIFIED/OH_PENDING** (20 testes, [protocolo OH](v2/pilot_01/OH_OFFLINE_EVIDENCE_GATE.md)); F4–F5 BLOCKED. Próximo gate depende de OpenHoldem real em ManualMode/OHReplay, não de novos testes autorreferenciais. Histórico V1 abaixo inativo.

# Roadmap vivo — 21/11/2026 (M08-RIVER4 fonte-first + G1/G6 de certificação separados / DRAFT)

| Gate | Estado | Critério de avanço |
|---|---|---|
| G0 Arquitetura | APROVADO | contratos mantidos |
| G1 Histórico/observação | ABERTO | replays reais de teste, divergências e fallback seguro |
| G2-a Pré-flop RFI / VS_OPEN / VS_3BET | HOLD | revisar mãos e contabilidade do jogo; conferir compatibilidade de premissas; documentar decisão |
| G2-b VS_4BET/5BET, squeeze, limps, outros stacks | BLOQUEADO | liberar G2-a primeiro |
| G3 Pós-flop SRP HU | EM DESENVOLVIMENTO | heurística inicial flop/turn/river em OpenPPL; validar reconhecimento de histórico e ação real antes de promover |
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

## Entrega pragmática RFI-MVP — interpretação dos gates
- **Objetivo permanece:** bot heurístico aproximadamente GTO, não solver científico nem tese de EV. Reusar charts compatíveis e heurísticas quando faltarem dados, sem inventar GTO certificado.
- Concluído **módulo RFI first-in com 845 casos/21 regras OpenPPL** a partir do histórico v0.6.1; 12 testes de paridade pragmática, preservação dos 5 mixes e do limp SB.
- **Próximo componente concreto:** gerar VS_OPEN a partir das 15 árvores existentes, com `RaiseTo`, `Call` e `Fold` compatíveis e mix `randomhand`, sem reimplementar mãos em Python.
- **Separação de gates:** criar estratégia em OPPL é permitido como artefato DRAFT, mas não liberar carga/operação real antes de OpenHoldem replay, controle de default.bot e ação final. Não liberar G2-b/VS_4BET antes da decisão G2-a.

## VS_OPEN-MVP — entrega OpenPPL sem mudança de estratégia (20/11/2026)
- RFI-MVP e VS_OPEN-MVP são ramos DRAFT prontos em fonte OpenPPL comum, não um bot operando. O combinado contém **142 regras**, 3.380 decisões de classe/nó, preserva 15 políticas VS_OPEN e 5 posições RFI do snapshot v0.6.1.
- **Próxima entrega útil:** portar VS_3BET (15 confrontos ×169) à mesma fonte OpenPPL, sem ajustar ranges ou desbloquear G2-b/VS_4BET. Proteger ações mistas com `randomhand`, legalidade do RaiseTo e eventos de reavaliação.
- **Teste mínimo para promoção futura:** integração OpenHoldem real via ManualMode/OHReplay offline, checagem de first raiser, pot 4 BB, to_call e stack + **ação final**; impedir fallback silencioso. Sem essa prova, manter G1 ABERTO e G6 PENDENTE. Não prolongar auditorias de equidade hipotéticas sem dados novos.

## Entrega de engenharia VS_3BET-MVP (20/11/2026)
- Portadas as 15 respostas às 3-bets de vilões sobre nosso RFI, usando OPPL com 135 regras, 888 cenários de mão realmente alcançáveis, 1.647 explicitamente sem regra; CSV 2.535 linhas. Fonte pré-flop integrada RFI+VS_OPEN+VS_3BET com **277 regras em uma função**.
- **Encerra somente o trabalho de transposição estática dos três módulos já disponíveis**, não aprova G2-a nem runtime. Testes 23 novos; esperado CI 277.
- **Próxima ação prática:** replay offline de 3–5 estados RFI/VS_OPEN/VS_3BET no OH-alvo para conferir guardas do 2º ato, randomhand e ação final; registrar fallback controlado antes de habilitar código em mesa. Após esse gate, implementar o núcleo pós-flop SRP HU (G3), preservando o projeto heurístico. Não abrir VS_4BET/G2-b enquanto bloqueado.
- **Critérios de parada:** não investir mais em análises hipotéticas que não alteram decisões; não obrigar EV solver para cada heurística; não chamar rascunho OpenPPL de bot validado.

## Avanço G3 pós-flop SRP HU — MVP 20/11/2026
- Desenvolvida cobertura prática de flop/turn/river em [portability/srp_hu_mvp/](portability/srp_hu_mvp/) (33 regras + cinco helpers) e montado arquivo OpenPPL único pré-flop + G3.
- Sem nova pesquisa de GTO/EV, sem alteração de range/sizing pré-flop: **a missão é bot heurístico jogável e coerente**, não solver científico.
- **Gate de qualidade pragmático:** símbolos corretos, classificação SRP suficiente sem roteamento incorreto, check/call/raise legal, fallback controlado e regressão de decisão. Replays em OpenHoldem offline seguem necessários para integração, não para provar GTO.
- **Próximo bloco concreto:** replay com histórico real e revisão das guardas `NumberOfRaisesBeforeFlop`/`BotCalledBeforeFlop`/ `OpponentsOnFlop`; depois melhorar textura/line postflop e liberar outros pot types por gate. A identificação de isolamento de limper permanece ambígua; bloquear promoção até abordagem definida.
- G1 ABERTO, G2-a HOLD, G2-b BLOQUEADO, G3 EM DESENVOLVIMENTO, G6 PENDENTE. Evitar bloqueio prolongado por auditoria científica, mas não fingir teste de runtime.

## Prioridade G3-HIST — Bot completo com histórico, não solver
**Fonte de verdade:** [STRATEGY_ARCHITECTURE.md](STRATEGY_ARCHITECTURE.md). Não limitar o alvo a heurísticas genéricas ou apenas 33 regras. O produto precisa de árvore extensível com milhares de caminhos **válidos**, condicionados pela cronologia completa, textura, SPR, posições, oponente, apostas e tipos de pote; qualificação de GTO é aproximada e heurística.
- **HIST-1 entregue em DRAFT:** nove caminhos de três histórias por street, 24 helpers / 58 regras pós-flop, 18 testes novos, sem alterar os 277 ramos pré-flop nem a v0.6.1.
- **HIST-2:** discriminar bet/raise/call em cada orbit, check-raise, 2+ raises, delayed c-bet e limp/iso histórico. **HIST-3:** board texture/runout, SPR, sizing buckets e river range/catcher. **HIST-4:** HU 3-bet/4-bet, limped pots, multiway e oponente adaptativo.
- **Critérios de parada pragmáticos:** não fabricar caminhos impossíveis ou jogar default em histórico desconhecido; não declarar excelência antes de observar qualidade e falhas; não exigir solver/EV formal por ramo para continuar DRAFT. G1/G2-a e G6 preservados; replay real ainda pendente.

## G3-HIST-v2: 36 trajetórias, mais perto da árvore completa
- **HIST-2 parcial entregue:** categorias B/C/X/R/H/M por street anterior, 36 pares flop/turn, 75 regras de ação e 70 funções. Mais 18 testes, 313 previstos no CI; módulos históricos preservados.
- **HIST-2 ainda NÃO finalizado:** os flags agregados OH não provam a ordem exata nem tratam múltiplos raises, limp/iso e squeeze; exigir reconstrutor cronológico confiável em replays offline antes de classificar todos os caminhos como alcançáveis e válidos.
- **Próxima engenharia sem mudança de direção:** HIST-2b evento/ação ordenada e pot-type → HIST-3 board texture/runout + SPR/size buckets → HIST-4 potes 3bet/4bet/multiway e oponente. Criar nós e heurísticas conforme significado estratégico; não somente multiplicar condições. G1/G2-a/G6 intactos.

## HIST-v3: avaliação de completude por eventos, não por produto de flags
- 36 funções HIST-v2 eram a multiplicação de 6 classificações agregadas e **não** representavam o universo de históricos. HIST-v3 materializa **484 palavras cronológicas possíveis** com até 4 raises por street para SRP HU, IP/OOP e PFR/caller; tem 31 testes de legalidade, colisão e compatibilidade de código.
- 3 colisões IP identificadas; registradores `Set user` + `BotsLast*Action` usados no rascunho OpenPPL; corrigida hipótese incompatível de `OpponentCalledOnFlop/Turn` para raises após bet do vilão.
- **Próximo gate G3-HISTv4:** capturar e testar por replay a sequência **realmente resolvida** (incluindo call/raise final), preservar preço/sizing por ação, distinguir pot-family SRP/3bet/4bet/limp/iso e efetivo SPR. Exigir cobertura de cada estado alcançável com ação contextual ou lacuna explícita; depois segmentar board texture/runout, posições e perfis adversários. Não gerar milhares de regras repetidas apenas para aumentar número.
- **Critério de parada/promover:** sem a versão do OH instalada + replay sem apostas + sem fallback não controlado, HIST-v3 é DRAFT. G1 aberto, G2-a HOLD, G6 pendente; manter meta de bot heurístico completo e análise pragmática, não solver.

**Priorização quantitativa G3 (HIST-v3):** [relatório de cobertura](portability/srp_history_v3/HIST3_ROUTING_COVERAGE.csv) demonstra 100/484 históricos legíveis no domínio sob fonte OPPL hipotética e **384 lacunas** (264 flop, 120 turn). Próximo avanço deve conectar eventos reais/provenientes e preencher famílias de linhas com políticas relevantes — não confundir lista enumerada com cobertura operacional. 36 testes HIST-v3, 349 totais previstos; G3 em desenvolvimento, G6 pendente.

## CRITÉRIO MÍNIMO DE PRODUTO: superar R10d — ADR-028 (20/11/2026)
- **Gate de não entrega**: nenhum release Heuristic6max como bot completo/excelente enquanto não cobrir funcionalmente as 14 famílias da [matriz](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv), com âmbito comprovadamente maior (especialmente 4–6 jogadores) e replays OH de ação final. R10d é referência de cobertura, não política a importar.
- **Realidade atual:** 14 famílias NÃO verificadas completamente, R10d substantivamente mais abrangente; não apresentar 484 trajetórias enumeradas como decisões reais. Preflop RFI/VS_OPEN/VS_3BET continua DRAFT; G2-a HOLD e G2-b BLOQUEADO para alterações estratégicas.
- **Entrega imediata neste checkpoint:** 3bet pot HU (15/13/11 ações flop/turn/river), dois marcadores de origem preflop, integrados sem mudança de ação anterior. Não inferir validação runtime pelos 27 novos testes.
- **Sequência racional:** (1) provar classificação de pote/ator e histórico observado; (2) expandir múltiplos tipos de pote e multiway 3way antes de otimizar raridades; (3) expandir 4–6 players, 4bet/5bet, limp/iso, all-in/short/deep stacks; (4) força/textura/runout/SPR/oponente; (5) avaliação prática e ambiente OH desconectado; (6) só então release. Manter milestones e critérios de parada por invalidez do histórico ou fuga de estado.

## SRP 3-way — ampliação sem descaracterizar piso R10d
- Após 3bet HU, foi implementada a primeira árvore multiway SRP com **exatamente 3 jogadores vivos no flop e turn/river**, 31 ações DRAFT e 33 marcadores de call como origem pré-flop. Guardas excluem 4bet/3bet, all-in e 4+ jogadores.
- **M05 = PARTIAL, não VERIFIED**, na [matriz de 14 capacidades](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv). Meta mínima de superar R10d continua BLOQUEADA, sem alterar G2-a HOLD.
- Próximos ganhos: multiway 3way que vira HU ao longo da mão, 3bet multiway, 4–6 jogadores, pote limp/iso e 4bet/5bet; então histórico completo, textura, SPR, ranges por oponente, empates/stack-offs. É proibido reduzir o escopo final para bater 392 testes.

## ADR-031 — gate prioritário de valor
Correção de quatro ramos de flop/turn em 3bet HU e SRP 3way: após o raise opcional, um segundo ramo `HaveNuts Call FORCE` precisa vir antes do fold residual. Testes de overbet tornam-se obrigatórios para toda nova família. A meta de superar R10d não mudou; evitar árvores gigantes com defeitos estratégicos graves.

## Multiway-v2 e LIMP-BB-v1 — expansão planejada sem pivô (20/11/2026)
- DRAFT concluído: potes com 4–6 jogadores ainda ativos no flop/turn/river, e potes originalmente multiway que ficam HU; BB check versus um único limp (SB ou outra posição) com pós-flop próprio.
- Gates M04 (limp/iso) e M06 (multiway 4+) passam a PARTIAL. **P1 seguinte:** 3→2, 4→2/3 e 5→2/3/4 adversários, limp/iso verdadeiro e potes 3bet multiway. **P2:** 4bet/5bet, squeeze, short/deep stacks, SPR, textura/runout e adversário. Não ampliar ranges v0.6.1 sem justificativa.
- Piso R10d não atingido; 14 capacidades não verificadas, nenhuma operação real autorizada.

## Último bloco de engenharia — MWT3 / MLIMP2 / P3BMW1
- Concluído estaticamente: 53 topologias SRP de jogadores que saíram em streets distintas; 7 CHECKs BB contra 2–5 limpers; 39 ações limped pot multiway; 43 ações potes 3bet multiway, mantendo agressor/caller e transferências até HU.
- Gates reais: capturar `OpponentsOnTurn/OnRiver`, `BotCheckedPreflop`, origem PFR/caller, `NumberOfRaisesBeforeFlop`, sizing e ação final no OpenHoldem offline. **Não** inferir confiabilidade de 521 testes sintéticos.
- Próxima prioridade de código: **limp/iso-raise e resposta ao isolamento, coldcall/squeeze e potes 4bet/5bet**, seguidos de força/board/runout, SPR, perfil e histórico de bet/raise/call resolvidos. A meta superar funcionalmente R10d segue inalterada, com 14/14 capacidades não VERIFIED.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## ISO-1 — próximo incremento DRAFT, sujeito à CI e ao replay real
- Autoria source-first implementada para CO (1/2 limpers) e BTN (1/2/3 limpers), 5 marcadores de intenção, uma lista de ISO nova e 41 decisões pós-flop sobre 120 topologias legais. As decisões históricas v0.6.1 continuam inalteradas; não confundir *adição de política* com validação GTO.
- **Próximos gates de engenharia:** verificar primeiro funcionamento das ações/preços/memória `Set` em replay OH offline; ampliar SB/BB iso, coldcall e resposta ao isolamento; então squeeze e, após liberar G2-a, VS_4BET/5BET. Em paralelo introduzir textura/runout, SPR e sequenciamento das ações observadas. Stop rule: não publicar jogo operacional sem compatibilidade OH e fallback legal controlado.
- **CI confirmada:** 534 execuções, 522 distintas por suíte, 27 suítes no run 44853164836; o piso R10d e todas as 14 capacidades continuam sem aprovação final.

## BLISO-2 — expansão de domínio blind isolation (DRAFT)
- Ampliadas as cinco origens CO/BTN ISO-1 com **13 origens SB/BB** (SB 1–4 limpers, BB 1–5). `Check` gratuito do BB permanece em vigor para mãos fora da lista de ISO. Captura de origem exclusiva, 43 ações pós-flop e 120 topologias cronológicas. Os números descrevem código DRAFT e não provas de EV.
- **Gate CI estático aprovado:** 18 testes novos, 552 execuções / 540 deduplicadas em 28 suítes no [workflow 44858080418](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418); a legalidade dos 13 Raises ainda exige replay OH antes de release. O próximo desenvolvimento permitido é resposta contra isolamento e coldcall/squeeze **sem modificar os ranges já congelados**. G2-a precisa de evidência nova antes de VS_4BET/5BET. `PotSize/Calls/StillToAct`, memórias e ação final aguardam OpenHoldem offline.
- Manter as 14 famílias do R10d em PARTIAL/MISSING conforme matriz; nenhuma promoção automática para VERIFIED.

## ISODEF-1 — segundo avanço na família isolamento, gates inalterados
- Escopo DRAFT: BTN vs iso CO e BB vs iso BTN após exatamente 1 limp (2 cenários específicos, 3bet/call/fold) e 42 ações pós-flop com 12 topologias monotônicas. Não ampliar automaticamente a outros positions/limpers/heads-up squeeze com semântica de `Calls` ainda não medida no OH.
- CI estática aprovada: 21 novos testes, comparação R10d, integração determinística e SHA256; [workflow 44860943038](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038), 573 execuções / 561 deduplicadas por suíte, 29 suítes. Critério de parada: `FirstRaiserPosition`, `LastRaiserPosition`, `StillToAct`, `Raises`, `Calls`, `PotSize`, reset de tag e sizing sem prova OH implicam DRAFT, independentemente de teste verde.
- Próximo passo técnico recomendado: **prova de histórico e legalidade da ação OpenHoldem offline**; depois ampliar defesa multi-limper, coldcall não-iso/squeeze e board/SPR/runout observados, preservando G2-a HOLD para ranges ancestrais. 14/14 R10d continuam não verificados.

## Gate experimental OH-G1G6-1 — não ampliar estratégia antes de observar o motor
- **Entrega realizada:** evidência offline G1/G6 preparada (10 casos/campos, versão e SHA do exe/fórmula/tablemap, debug, dois pares .html/.bmp, log Basic Info com ação calculada e tomada, integridade e restrições privadas). [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886): 599 execuções, 587 deduplicadas, 30 suítes; 26 testes novos. Nenhuma regra estratégica mudou.
- **Gate A / G1:** usuário disponibilizar versão real da aplicação e tablemap, debug com contadores observados e capturas pré-flop→flop→turn→river + mudança de mão. Confrontar `Calls`, `Raises`, `StillToAct`, `NumberOfRaisesBeforeFlop`, `Set user_*` com histórico verdadeiro. Se valores instáveis, **corrigir contrato** antes de desenvolver squeeze/4bet.
- **Gate B / G6:** demonstrar fórmula efetivamente carregada, `Best action`, `Action taken`, sizing legal em BB e *estado posterior aceito por simulador offline*; reprodução de fallback e no-match. OHReplay estático e ManualMode isolados são evidência parcial, não fechamento automático.
- **Critério de parada:** sem captura autêntica ou com divergência não explicada, manter DRAFT e G1/G6 abertos, 14/14 R10d sem aprovação; G2-a HOLD e ranges anteriores intactos. Próximo trabalho permitido: diagnosticar a compatibilidade, não acrescentar mais dezenas de políticas não observadas.

## OH-SRC1 — construção e certificação são trilhas separadas (ADR-040)
- **Trilha de construção (NÃO requer hash de OH local):** consultar código-fonte C++/OpenPPL e testar a mesma fonte estratégica. [CI OH-SRC1](https://github.com/pmartins87/Heuristic6max/actions/runs/44864070437) aprovou 17 novos testes (616 execuções / 604 deduplicadas, 31 suítes). `OH-SRC1` mediu 436 igualdades exatas `PotSize`; próximo gate é classificar colisões dos 15 valores por pote/tipo de ação. **Não trocar por tolerâncias globalmente** nem ampliar squeezes/4bet a partir de `Calls` desconhecido.
- **Trilha de certificação de produto (não necessária para continuar construindo):** runtime OpenHoldem, parsing verdadeiro, reset da mão, captura do símbolo, ação final e fallback. Identidade da instalação/hash só é relevante se se quiser provar uma build particular; nenhum dado desse tipo impede pesquisa e desenvolvimento.
- **Critério de mudança:** alterar os guardas de pote somente com justificativa por domínio, reinterpretação fonte-first e testes de inclusão/exclusão (sem vazamento a outro contexto ou estratégia); preservar v0.6.1. Sem comprovação real, manter G1/G6 não aprovados e R10d 0/14, mas **não bloquear automaticamente a evolução de código por isso**.

## CI-LEAN1 — gate de produtividade sem mudar a estratégia (ADR-041)
1. **Desenvolvimento:** selecionar uma lacuna estratégica material na matriz R10d, definir estados/ações aceitos, construir um único incremento nativo OpenPPL e testar a família impactada; sem hash do OH local como bloqueador.
2. **Integração:** manter PR em `draft` durante mudanças intermediárias. Marcar `ready_for_review` quando o incremento estiver consistente; exigir regressão integral com status `success` no commit exato antes de merge. Nova versão cancela run obsoleto apenas da própria PR. CI integral também em `main`.
3. **Parada:** não criar verificadores de verificadores nem reexecutar R10d em cada ancestral; só adicionar teste quando o risco da nova regra for concreto. Preservar precedência/fallback/linhagem OpenPPL, ranges congelados e gates de promoção.
**Métricas do processo:** 126→113 etapas, R10d 6→1 comparações, suíte R10d 2→1. **Métrica do produto:** avançar em 14 capacidades R10d, hoje 0 verificadas integralmente.

## M08-RIVER4 — entrega concreta, próximos passos proporcionais
- Fonte integrada `portability/river_fourflush_v1/river_fourflush_integrated_draft.oppl`, 4 decisões estritamente no river four-flush SRP HU sem flush/nuts, com 2.007 WHEN anteriores preservadas. M08 permanece PARTIAL porque não inclui paired runouts, one-card-straights, outras famílias de potes, EV nem prova de motor.
- Avaliar a alteração via 7 testes fonte-first, uma CI completa em PR pronta e outra na main. **Próxima prioridade estratégica:** outro runout adverso (straight/paired) ou SPR com condição comprovadamente mal tratada; não criar mais camadas de auditoria.
- Manter v0.6.1, G2-a HOLD, G1/G6 pendentes e 0/14 R10d VERIFIED; não usar a nova branch para antecipar VS_4BET/5BET.
