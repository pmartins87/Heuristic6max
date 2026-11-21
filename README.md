# Heuristic6max — fonte de verdade

## Checkpoint MWT3 + MLIMP2 + P3BMW1 — OpenPPL integrado (20/11/2026)
- [Transições SRP multiway](portability/multiway_transitions_v3/README.md): 53 topologias intermediárias e **41 decisões pós-flop** entre quatro e seis jogadores no flop, com contagens próprias de turn/river.
- [BB contra 2–5 limpers](portability/multilimp_bb_v2/README.md): **7 opções pré-flop de CHECK** e **39 novas decisões pós-flop**, com distinção se o SB completou.
- [3bet multiway](portability/p3bet_multiway_v1/README.md): **43 novas decisões pós-flop** para agressor ou caller pré-flop em potes 3bet com 3–6 jogadores no flop.
- [Fonte única integrada](portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl): **1.460 WHEN, 136 funções, 187 listas, 99 SET, 16 flags user_**. Mais 38 testes (total **521 previsto na CI**), nenhum range da v0.6.1 alterado.
- **Bot ainda incompleto:** 14/14 capacidades do piso DeepCrusher_R10d não foram plenamente verificadas; OH real e ação final não testados. Não confundir cobertura estática com excelência ou prontidão operacional.

## Checkpoint ativo — Multiway-v2 + LIMP-BB-v1 (20/11/2026)
- [Fonte integrada OpenPPL mais recente](portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl), [multiway 4–6way e transições HU](portability/multiway_v2/README.md) e [BB check contra um limper](portability/limped_bb_v1/README.md).
- **74 regras de ação pós-flop multiway** (40 com 4–6 jogadores ativos e 34 para multiway→HU), mais **33 ações pós-flop limp-BB** e 2 novos Check FORCE pré-flop. **42 testes incrementais; 434 testes esperados na CI.**
- Integrado mede **899 WHEN / 106 funções f$ / 187 handlists / 92 Set user / 9 símbolos user_**. Os ranges e o histórico anterior permaneceram preservados.
- [Benchmark DeepCrusher_R10d](benchmarks/r10d_floor/README.md) permanece **NÃO ATINGIDO**: M04 e M06 avançaram de MISSING para PARTIAL; 14/14 capacidades ainda exigem validação completa. Sem execução OpenHoldem, sem liberação para jogo real.

## Novo progresso efetivo — pós-flop single-raised **3-way**
- [p3way_srp_v1](portability/p3way_srp_v1/README.md) adiciona **31 regras de ação OpenPPL** (13 flop/10 turn/8 river), com dois papéis: Hero abriu primeiro ou pagou o open. **33 condições VS_OPEN Call** geram registros de origem `Set user_H6_VSOpenCallIntent`, sempre confirmados contra BotCalledBeforeFlop/raises antes do uso posterior.
- [Arquivo integrado mais recente](portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl) reúne pré-flop RFI/VS_OPEN/VS_3BET, SRP HU, 3bet HU, SRP 3-way — **729 WHEN, 92 f$, 187 listas, 90 Set e 7 símbolos user_**, contra 6.021 WHEN e 561 símbolos user_ R10d.
- [Matriz de lacunas atualizada](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv): **M05, multiway 3 jogadores, evoluiu MISSING → PARTIAL**. **0/14 capacidades totalmente aprovadas**. Seguimos deliberadamente SEM alegar superar R10d; resta muito trabalho.
- **16 testes incrementais novos**, total previsto **392 = 349+15+12+16**. Sem alterações dos ranges/decisões pré-flop e sem validação executável OpenHoldem.

## Novo piso obrigatório: superar o DeepCrusher_R10d — requisito NÃO atingido
- [Comparação quantitativa da fonte real R10d](benchmarks/r10d_floor/README.md): R10d contém **6.021 WHEN, 725 funções, 545 handlists e 561 símbolos user_**; o arquivo integrado Heuristic com 3bet HU novo tem **649 WHEN, 88 funções, 187 handlists e 6 símbolos user_**. Métricas são referências de engenharia, **não prova de qualidade ou completude**.
- [Matriz de 14 capacidades mínimas](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv) e [relatório reproduzível](benchmarks/r10d_floor/CURRENT_GAP_REPORT.json). **14/14 requisitos ainda não estão integralmente verificados**; a release final está bloqueada até dominância funcional real e OpenHoldem seguro.
- [Nova família de pote 3-bet heads-up](portability/p3bet_hu_v1/README.md): **39 ações pós-flop** (15 flop, 13 turn, 11 river) + intenção RFI/3bet registrada em OpenPPL (9+44 situações), leitura do próprio código para testes, nenhuma alteração de ranges ou ações de pré-flop.
- **27 testes novos locais**, total esperado **376 (349+15+12)** em CI. Status: DRAFT, sem aprovação do executável OpenHoldem nem qualidade estratégica comprovada.

## HIST-v3 — história cronológica, sem inflar decisões (20/11/2026)
- [Fonte OpenPPL, testes e documentação](portability/srp_history_v3/README.md); [484 sequências legais flop→turn](portability/srp_history_v3/HIST3_484_CHRONOLOGICAL_PATHS.csv); [3 colisões por flags](portability/srp_history_v3/HIST3_OBSERVABILITY.csv).
- **484 = cenários legais de eventos com até quatro raises por street, não regras de ação prontas**, considerando IP/OOP e agressor/caller PF. Permite localizar as lacunas antes de escrever mais branches.
- **Correção real v2:** a implementação OpenPPL de `OpponentCalledOnFlop/Turn` exige `NoVillainBetOrRaised...` e portanto os helpers R/H anteriores podiam ser inalcançáveis. A v3 reclassifica R/H sem esse símbolo, usando continuidade da street, e introduz quatro memórias de eventos nativos para separar duas sequências IP agregadas de forma idêntica.
- **75 regras de ação preservadas**, +10 helpers e 4 capturas `Set user`; 31 novos testes, **344 testes esperados em CI**. Pré-flop e ranges não mudaram. Histórico ainda não verificado no OpenHoldem-alvo; G3 aberto, G6 pendente.

## Checkpoint mais recente — G3-HIST-v2: 36 trajetórias históricas (20/11/2026)
- [Módulo de histórico OpenPPL v2](portability/srp_history_v2/README.md) classifica **seis** sequências no flop e **seis** no turn, compondo **36 caminhos condicionais no river** (B=bet-call, C=check-through, X=call, R=raise sobre aposta, H=check-raise, M=bet-raise-call).
- **75 regras de ação pós-flop** (14 flop + 22 turn + 39 river), 70 funções OpenPPL e o mesmo pré-flop de 277 regras preservado. Estratégia única OPPL: o Python apenas combina e testa o mesmo texto; versão HIST-v1 preservada.
- **18 testes incrementais novos, 313 totais esperados no CI**; nenhuma mudança em ranges/snapshots v0.6.1. Excelência estratégica permanece uma meta de avaliação, não resultado demonstrado.
- **Não operacional:** estados desconhecidos podem usar fallback OpenHoldem; flags agregados não substituem histórico cronológico integral, e ainda faltam replays no executável alvo. [Arquitetura viva do bot completo](STRATEGY_ARCHITECTURE.md).

## Arquitetura do bot completo — G3-HIST-v1 (20/11/2026)
- **Meta de produto:** bot de engenharia complexa, milhares de caminhos por histórico, board, tamanho, posição, ranges e oponente; heurísticas inspiradas no GTO, **não um solver**. Excelência estratégica é objetivo, não resultado já medido. [Arquitetura viva](STRATEGY_ARCHITECTURE.md).
- [Implementação histórica OpenPPL](portability/srp_history_v1/README.md): três classes exclusivas de flop × três de turn = 9 sequências explícitas no river; 58 regras pós-flop (14 flop + 16 turn + 28 river), 24 funções; integração preserva as 277 regras pré-flop.
- **18 novos testes locais**, total CI esperado 295; os ranges de v0.6.1 e a base G3 foram preservados. Sintaxe, fallback e observações reais do OpenHoldem ainda NÃO foram validados; não operar em jogos reais.
- Este avanço é uma **fundação incremental** da árvore histórica, não sua conclusão. Próximo corte: raises, check-raises, sizings e linha canônica da mão, depois textura/SPR e potes complexos.

## G3 — MVP prático de pós-flop SRP HU (20/11/2026)
- [Fonte OpenPPL de flop/turn/river, documentação e testes](portability/srp_hu_mvp/README.md); [rascunho combinado pré-flop + pós-flop](portability/srp_hu_mvp/preflop_and_srp_hu_draft.oppl).
- **33 regras** de decisão (14 flop, 10 turn, 9 river), mais 5 helpers, em OpenPPL nativo; ações heurísticas de valor, draws, calls por sizing, checks/folds e c-bet seca com `randomhand`.
- **18 testes incrementais aprovados localmente**, fonte única OPPL; os 3 módulos anteriores e ranges v0.6.1 não foram alterados. CI verifica regressão e concatenador.
- Esta é uma **primeira árvore prática, NÃO um bot operacional**: classificação SRP por histórico OpenPPL tem limitações (possível limp/isolation), `None` fora do domínio não impede fallback do OpenHoldem, e não houve replays reais da ação final. G1/G2-a abertos, G3 EM DESENVOLVIMENTO, G6 pendente.
- Foco do projeto: **bot heurístico inspirado em GTO**, sem exigência de resolver GTO, simular EV ótimo ou desenvolver método científico; testes só para garantir consistência e evitar retrabalho.

## VS_3BET-MVP — árvore pré-flop em OpenPPL (20/11/2026; DRAFT)
- [Código, testes e contrato de integração](portability/vs_3bet_mvp/README.md); [mapeamento 15 × 169](portability/vs_3bet_mvp/VS3_2535_MAPPING.csv).
- **888 decisões alcançáveis** de 2.535 classes/confrontos, 1.647 impossíveis após RFI (nenhuma ação inventada). **90 handlists + 135 regras**, 23 testes novos; baseline RFI/VS_OPEN/VS_3BET v0.6.1 **intacta**.
- [Fonte OpenPPL VS_3BET](portability/vs_3bet_mvp/vs_3bet_6max_mvp.oppl) e [fonte única pré-flop RFI+VS_OPEN+VS_3BET](portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl): **277 regras** com um só `f$preflop`. Cobrem apenas sizings/árvores 100BB previstos, **não** são bot operacional.
- Escolhas técnicas: `Raises=1` (contagem só dos adversários), `BotRaisedBeforeFlop`, `RaisesSinceLastPlay=1`, posições de primeiro/último raiser e stack no início da rodada. Sem replay real OH nem fallback controlado: G1 aberto, G2-a HOLD, G6 pendente.
- **Foco prático:** bot heurístico aproximadamente GTO, sem solver próprio ou prova científica de EV. Regressões servem para não quebrar transcrição e histórico.

## VS_OPEN-MVP: 15 árvores pré-flop em OpenPPL (DRAFT — NÃO operacional)
- [Código, regra de escopo e 19 testes](portability/vs_open_mvp/README.md), [fonte VS_OPEN das 2.535 decisões](portability/vs_open_mvp/vs_open_6max_mvp.oppl) e [pré-flop combinado RFI + VS_OPEN](portability/vs_open_mvp/preflop_rfi_vsopen_draft.oppl).
- **15 confrontos × 169 classes = 2.535 estados**, 81 listas disjuntas por confronto, 121 regras OpenPPL de VS_OPEN; combinadas com 21 regras RFI anteriores = **142 regras na mesma função preflop** e 3.380 estados de classe/par ou classe/posição.
- Ações 3BET/CALL/FOLD e todos os mixes `randomhand` copiados sem alterações da v0.6.1; guardas `Raises=1`, `Calls=0`, `FirstRaiserPosition` e `LastRaiserPosition` + tamanho de open, call e stack. 3bet RaiseTo 8, 10.25 ou 9.6 BB.
- **19 testes incrementais**; **273 testes acumulados esperados na CI**. Sem replay em OpenHoldem ou fallback seguro; G2-a HOLD em estratégia, G6 pendente. Próximo módulo: VS_3BET sobre snapshot intacto.

## RFI-MVP 6-max — módulo OpenPPL das cinco posições (20/11/2026)
- **[Fonte OpenPPL e documentação](portability/rfi_mvp/README.md)** · [845 linhas por mão/posição](portability/rfi_mvp/RFI_6MAX_845_MAPPING.csv).
- Implementadas 5 posições LJ/HJ/CO/BTN/SB, **845 classes de situação**, 21 regras e os cinco mixes por `randomhand`; SB preserva ramo de limp (`Call`), não apenas raise/fold.
- Fonte estratégica OpenPPL única; Python offline apenas gera/verifica. Frequências e decisões da **v0.6.1 são integralmente preservadas**.
- **12 testes novos** (254 acumulados esperados no CI), sem novas pesquisas de EV imaginário. **Não é bot operacional completo**: VS_OPEN/VS_3BET, fallback e pós-flop pendem; OpenHoldem real não foi executado.
- **Prioridade de engenharia:** converter VS_OPEN a partir das tabelas existentes, mantendo gate de integração OH separado do desenvolvimento da heurística.

## PORT-3 / RPL-0 — auditor de evidência OpenHoldem (sem aprovação de runtime)
- [Método, provas e instruções offline](portability/port3/README.md), [auditor Python](portability/port3/replay_audit.py), [27 testes](portability/port3/test_replay_audit.py).
- O auditor lê o **mesmo arquivo OpenPPL PORT-2**, exige `randomhand` observado, símbolo/estado do replay, SHA da fórmula, **ação da fórmula** e **ação final**. Recusa no-match como fail-closed e detecta fallback/sizing divergente.
- **Nenhuma captura OH real foi produzida**. CSV sintético contém **5 `STATIC_ONLY` e 1 `BLOCKED_NO_MATCH`**; não há `PASS` operacional automático, mesmo com arquivo de evidência. A versão de OH, logs e observações reais seguem pendentes.
- 27 testes incrementais; **242 testes esperados em CI** = 215 anteriores + 27. Preservados todos os ranges/snapshots v0.6.1; G1 aberto, G2-a HOLD, G6 pendente.

## PORT-2: mix nativo OpenPPL com `randomhand` (estático, NÃO operacional)
- [Fonte única OpenPPL, interpretador e 19 testes](portability/port2/README.md); [mapeamento das 169 classes LJ](portability/port2/PORT2_LJ_169_MAPPING.csv).
- KJo: raise 40% quando `randomhand < 0.40` e fold 60% caso contrário; 43 classes com raise puro, 125 com fold puro, **nenhuma mudança na baseline v0.6.1**.
- 19 testes incrementais; total de **215 testes esperados no CI** (196 anteriores + 19). São testes de fonte estática, **não testam o OpenHoldem real**.
- PORT-2 **parcial**, sem promoção operacional: estabilidade/valor do símbolo no OH instalado, fallback, scraping e sizing final seguem exigindo replay em ambiente sem apostas.

Estratégia **heurística** de No-Limit Hold'em cash 6-max baseada em fundamentos de GTO, com contratos, ranges auditáveis e testes reprodutíveis. **Não é um solver; não é um bot operacional validado; não há comprovação de EV ou winrate.**

**Checkpoint ativo: piso obrigatório DeepCrusher_R10d e potes 3bet HU + SRP 3-way (20/11/2026)** — Heuristic6max ainda NÃO supera R10d, é DRAFT; G1 aberto, G2-a HOLD e G6 pendente.

## PORT-1 parcial — RFI LJ (20/11/2026)

- [Código OpenPPL, testes e fonte única](portability/port1/README.md), [cobertura das 169 classes](portability/port1/PORT1_LJ_169_MAPPING.csv).
- 43 RAISE puros e 125 FOLD puros representados em duas listas/regras OpenPPL; **KJo (40% raise/60% fold) permanece NÃO MAPEADO** para não quebrar a estratégia mista.
- 15 testes incrementais em Python interpretam as regras OpenPPL diretamente, sem estratégia paralela. Contagem total esperada 174+7+15 = **196 testes**.
- **PORT-1 permanece ABERTO**, pois símbolos, sorteio estável, ação ilegal e fallback ainda precisam de teste no OpenHoldem real. Nenhum range estratégico mudou.

## Auditoria v0.11 — charts públicas, sem substituir ranges
- [Método, fontes e critérios](audits/g2a_v0_11/README.md)
- [Fontes e premissas registradas](audits/g2a_v0_11/source_candidates.json)
- [Vereditos reproduzíveis](audits/g2a_v0_11/SOURCE_APPLICABILITY_v0_11.csv)
- Três fontes examinadas; **nenhuma apta à substituição direta** no cenário HJ abre 2,5 BB e CO 3-bet para 8 BB. Rake/cap alvo não documentados.
- **174 testes locais aprovados**, 11 novos na auditoria; nenhuma estratégia modificada.
- **Linguagem:** motor Python. OpenPPL/OpenHoldem permanece G6 pendente, sem código executável.
- **Critério de parada:** não prolongar toy-EV/EQR de parâmetros não calibrados sem nova evidência.

## Retomada em novo chat ou IA
Leia, nesta ordem:
1. [PROJECT_STATE.md](PROJECT_STATE.md)
2. [ROADMAP.md](ROADMAP.md)
3. [DECISIONS.md](DECISIONS.md)
4. [HANDOFF.md](HANDOFF.md)
5. [CHANGELOG.md](CHANGELOG.md)
6. [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md)


## Auditoria v0.10 — HJ/CO equities, sem mudança estratégica
- [Método e referência v0.10](audits/g2a_v0_10/README.md), [169 equities por classe](audits/g2a_v0_10/HJ_CO_EQUITY_169_REFERENCE_v0_10.csv), [15 conferências Monte Carlo](audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv).
- A fonte privada fornecida tinha 1.624.350 confrontos físicos ordenados, cobertura/reciprocidade conferidas; licença/autoria não documentadas, portanto **não publicar o bruto**. SHA-256 da fonte e método presentes no README da auditoria. Motor MC em Python stdlib pode reestimar sem a fonte original.
- Ex.: AQo 41,3101%, AJo 35,6951%, KJo 32,3099%, TT 44,0217% de **equidade bruta de showdown** contra a política 3bet do CO. Isso NÃO determina EV de call fora de posição, nem prova que folds existentes estão errados.
- 10 testes novos; total acumulado previsto **163 (124+7+11+11+10)**. Todos os ranges e o snapshot v0.6.1 permanecem intactos; G1 aberto, G2-a HOLD, G2-b bloqueado.

## Auditoria G2-a v0.9 — HJ vs CO, preços e contrafactuais (sem alterar ranges)
- [Método, limites e decisão](audits/g2a_v0_9/README.md)
- [169 classes com posterior e exposição à 3-bet](audits/g2a_v0_9/HJ_CO_169_CLASS_SCREEN_v0_9.csv)
- [15 classes candidatas: RFI vs resposta ao 3bet](audits/g2a_v0_9/HJ_CO_CANDIDATE_COUNTERFACTUALS_v0_9.csv)
- [36 fronteiras hipotéticas: rake/realização/sizing](audits/g2a_v0_9/HJ_CO_PRICE_FRONTIER_v0_9.csv)
- [Fonte e 11 testes incrementais](audits/g2a_v0_9/hj_co_frontier.py)

**153 testes previstos e verificáveis** (124+7+11+11). HJ/CO: FOLD 77,5377%, CALL 14,0392%, 4BET 8,4231%. Com abertura 2,5 e 3-bet para 8 BB, call adicional 5,5 BB / pote 17,5 BB = 31,43% de equidade imediata sem rake. Os cenários NÃO estimam equidade real, EV ou uma estratégia GTO; nenhum range foi alterado. G2-a HOLD.

## Auditoria G2-a v0.8 — defesa por mãos e interferência de terceiros (sem alterar ranges)
- [Método e resultados v0.8](audits/g2a_v0_8/README.md)
- [Mãos de maior contribuição aos folds](audits/g2a_v0_8/TOP_FOLD_CLASSES_8_v0_8.csv)
- [Famílias em 15 nós](audits/g2a_v0_8/DEFENSE_FAMILIES_15_v0_8.csv)
- [Sensibilidade a cold actions](audits/g2a_v0_8/COLD_ACTION_SENSITIVITY_15_v0_8.csv)
- [Código e 11 testes v0.8](audits/g2a_v0_8/defense_composition.py)

**142 testes locais** (124+7+11). Exemplo HJ-CO: **58,1119 pontos percentuais dos folds** vêm de quatro famílias (suited-outras, pares 22–66, broadways offsuit sem A e Ax offsuit). Isto NÃO significa que essas mãos deveriam dar call. Em BTN-SB, a pressão isolada anterior (+0,048 BB) desaparece sob pequena interferência hipotética do BB (~0,49%). Sem simulação de EV real; G2-a permanece HOLD.

## Auditoria G2-a v0.7 (sem alterar ranges)
- [Método e conclusões](audits/g2a_v0_7/README.md)
- [15 nós: fold contra preço da 3-bet](audits/g2a_v0_7/3BET_PRESSURE_ALL_15_v0_7.csv)
- [8 nós: detalhamento por mãos físicas do agressor](audits/g2a_v0_7/3BET_PRESSURE_HANDS_8_v0_7.csv)
- [Script e testes](audits/g2a_v0_7/pressure_audit.py)

7 dos 8 nós críticos exibem EV positivo para **blefe de equidade zero no experimento isolado**, sem cold actions e com Hero continuando = perda integral do investimento. **Não é EV real, não prova GTO nem autorização de alteração de estratégia.** O resultado altera a prioridade da revisão: investigar folds e defesas conjuntas (call + 4bet), não somente percentual de 4bet.

## Código e dados completos no GitHub
- [v0.5 — 51 arquivos históricos preservados](gto6_heuristic_v0_5/)
- [v0.6 — 61 arquivos históricos, com errata de manifesto](gto6_heuristic_v0_6/)
- [v0.6.1 — 66 arquivos autocontidos; 124 testes; correção de integridade](gto6_heuristic_v0_6_1/)
- [Método e achados G2-a](gto6_heuristic_v0_6_1/G2A_METHOD_AND_FINDINGS_v0_6.md)
- [8 confrontos marcados para revisão](gto6_heuristic_v0_6_1/G2A_MAJOR_REVIEW_8_NODES_v0_6.csv)

Os **fontes e CSVs completos** agora estão commitados no repositório. Os arquivos ZIP são conveniências para transferência; não são necessários para reconstrução a partir do GitHub.

## Como verificar
    python scripts/check_repository.py
    cd gto6_heuristic_v0_6_1
    python -m unittest -q
    python vs3_blocker_audit_v0_6.py

**Regras permanentes:** alterar docs vivos após cada decisão; preservar versões; não igualar benchmarks incompatíveis artificialmente; política ausente deve retornar None, nunca Fold/Check silencioso; manter DeepCrusher/CrusherTBP intactos; não operar em mesas com dinheiro real até validação apropriada.

Issues: [#1 — importação concluída](https://github.com/pmartins87/Heuristic6max/issues/1) e [#2 — auditoria estratégica aberta](https://github.com/pmartins87/Heuristic6max/issues/2).

**Errata de rastreabilidade:** v0.6 marcou equivocadamente 51 arquivos ancestrais como SAME após regerar o manifesto. A v0.6.1 confirma **50/50 fontes de conteúdo idênticas** e 1 manifesto regenerado. Ver [ERRATA](gto6_heuristic_v0_6_1/ERRATA_v0_6_1.md).


## PORT-0: novas regras devem ser portáveis na origem (ADR-016)
- [Contrato de portabilidade](PORTABILITY_CONTRACT.md): usar regras nativas OpenPPL ou uma representação declarativa que gere OpenPPL e simulação Python a partir da mesma fonte. Python de auditorias e testes permanece livre.
- [Piloto com 2 regras OpenPPL](portability/portable_rfi_probe.oppl), [intérprete Python](portability/oppl_probe.py) e [7 testes](portability/test_oppl_probe.py) em 3.042 estados. Não operacional e ainda sem testes no OpenHoldem real.
- Bloqueados até paridade demonstrada: mistura SHA256/Random, predicado source_quality=HIGH, None versus fallback automático e ajustes de RaiseTo ilegal.
- Versões e ranges anteriores permanecem preservados; G6 continua uma etapa futura.

### HIST-v3 — medição de cobertura por interpretação da mesma fonte OPPL
- [Relatório de 484 linhas](portability/srp_history_v3/HIST3_ROUTING_COVERAGE.csv) e [auditor de cobertura](portability/srp_history_v3/routing_coverage.py): **100 domínios admissíveis sob hipóteses estáticas de biblioteca, 384 lacunas (264 flop, 120 turn)**.
- **100 não significa 100 decisões verificadas nem 100 exemplos vistos no OpenHoldem**; a simulação supõe que a captura de memória anterior ocorreu corretamente. 484 é universo de palavras legais, não número de políticas.
- +5 testes de cobertura e determinismo: **36 testes HIST-v3 e 349 testes totais esperados CI**. Próximo passo: resolver lacunas por famílias de histórico realmente observáveis; não gerar ramos sem proveniência.

## Hotfix estratégico ADR-031 — prioridade de nuts sobre overbet
Uma overbet muito grande podia escapar do call genérico e atingir `Fold FORCE` mesmo com `HaveNuts`. Corrigidos flop e turn de 3bet HU e SRP 3way: `HaveNuts` agora possui Call prioritário após o raise opcional. **41 ações 3bet HU (16/14/11) +33 SRP 3way (14/11/8)**, 74 novas ações; 733 `WHEN` na fonte integrada. Testes incluem overbets maiores que 250% do pote. Ranges pré-flop intactos; R10d continua NÃO SUPERADO; OH real não testado.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## ISO-1 — expansão DRAFT de isolamento de limpers
- [Módulo de isolamento CO/BTN contra 1–3 limpers](portability/iso_raise_v1/README.md): cinco contextos pré-flop novos, 41 decisões pós-flop e 120 topologias; ranges RFI/VS_OPEN/VS_3BET anteriores preservados. O novo integrado permanece **DRAFT, não operacional**; 13 testes incrementais aguardam CI, e o piso funcional R10d permanece bloqueado.
