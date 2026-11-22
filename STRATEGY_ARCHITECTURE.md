> **ARQUITETURA V2 ATUAL — ADR-050:** ver [fonte completa de estratégia](v2/bot/DeepPoker_V2_Cash6max_v0_1.oppl), [guia](v2/bot/README.md), [Política Geral](v2/GENERAL_POLICY.md) e [Plano Vivo](v2/PLAN.md). O módulo único inclui pré-flop, flop, turn e river, 16 handlists, helpers de valor/draw/SPR/história e fallback explícito; evolução orientada por literatura profissional e feedback de hands reais, sem copiar o short-stack do R10d e sem gates científicos a cada regra.

> **ARQUITETURA V2 — ADR-049:** interpretar exemplos como princípios gerais via [política geral](v2/GENERAL_POLICY.md); consultar [auditoria R10d](v2/DEEPCRUSHER_TRANSFER_AUDIT.md). A unidade de avanço é **família de estados alcançáveis com decisões por classes/contexto**, não duas cartas físicas ou percentual fixo. Priorizar integridade de mão/história, ranges, preços, SPR e coerência entre streets; F1/F2 paralelos à validação OH. O texto abaixo conserva arquitetura e histórico anterior.

> **ARQUITETURA V2 — ADR-048:** [Plano Vivo](v2/PLAN.md). Separação de contexto/ação mantida; [duas ações exatas OpenPPL](v2/pilot_01/README.md) passam 20 testes simbólicos de precedência e exclusão, mas falta [replay OH real](v2/pilot_01/OH_OFFLINE_EVIDENCE_GATE.md). Não generalizar os 2 spots, não copiar V1 nem tratar no-match Beep como proteção suficiente.

# Heuristic6max — arquitetura de um bot COMPLETO, sensível ao histórico

**Fonte de verdade do objetivo e escopo — 20/11/2026.** O projeto é **um bot de poker de engenharia complexa**, com milhares de caminhos de decisão e heurísticas inspiradas no GTO. Não é um solver nem um experimento científico. **Excelência estratégica é a meta**, nunca uma propriedade presumida pela quantidade de regras ou testes.

## Núcleo da estratégia (requisito, não simplificação)

Cada decisão precisa ser condicionada por: street, quantidade/posição dos jogadores, tipo de pote e árvore pré-flop, papel do Hero (agressor/caller), histórico da mão (ações do Hero e dos oponentes em ordem e tamanho), SPR/stack efetivo, textura de board e runout, força relativa da mão/draws/blockers, frequência/size de apostas e comportamento observado do adversário. Sem esse histórico, uma regra genérica de “top pair” é uma exceção conservadora/provisória, não arquitetura final.

A unidade de implementação é um **nó de um grafo de decisões**, não um número fixo de ifs independentes. Cada nó tem chave canônica, evidências de estado, ações legais, tamanho/frequências, histórico anterior, política de prioridade, marcador DRAFT/VERIFIED e testes específicos. Não criar estados impossíveis só para inflar a contagem. Reutilizar helpers e handlists OpenPPL para centenas/milhares de combinações efetivamente alcançáveis.

## Eixos de cobertura (expansão gradual sem pivô)

| Eixo | Famílias exigidas no produto final | Situação no checkpoint atual |
|---|---|---|
| Pré-flop | RFI, VS_OPEN, VS_3BET, VS_4BET/5BET, limp/iso, cold-call, squeeze, shove, stacks variados | RFI/VS_OPEN/VS_3BET DRAFT; demais pendentes |
| Tipos de pote | SRP, 3-bet, 4-bet, 5-bet, limp/iso, multiway | SRP HU parcial |
| Streets | Flop, turn, river, incluindo transições e mudanças de iniciativa | Três streets em G3; HIST-1 adiciona duas transições explícitas |
| Linhas de aposta | check-through, bet-call, bet-raise, check-raise, delayed c-bet, double-barrel, probe/donk, raise-call, bets por tamanho | HIST-1 cobre apenas B/C/X simples × B/C/X simples (9 sequências) |
| Board | paired/unpaired, flush/straight draws/completed, conectividade, textura e mudanças no turn/river | Só sinais gerais no MVP G3 |
| Estratégia | value, bluff, semi-bluff, bluff-catch, blockers, proteção, equity realization, range advantage, pot odds e sizing | Heurísticas iniciais; estratégia ainda DRAFT |
| Adversários | posição, range, perfil, tendências por ação/tamanho, amostra mínima e fallback conservador | Não implementado |
| Operação | parsing OH, log de histórico íntegro, ações legais, no-match seguro e replays offline | Ainda bloqueado no executável real |

**Regra de decisão técnica:** completar um eixo não equivale a terminar o bot. Não alterar o baseline pré-flop para forçar taxa agregada de um benchmark incompatível. Dados novos mudam a política apenas após checagem coerente e regressão; não exigir estudo de EV rigoroso para cada heurística DRAFT. Priorizar perdas graves causadas por falhas de histórico, decisões ilegais, sizings e ausência de resposta.

## Continuidade implementada

- `gto6_heuristic_v0_6_1/` é a referência histórica preservada para RFI, VS_OPEN e VS_3BET.
- `portability/srp_hu_mvp/` é o pós-flop G3 original, igualmente preservado.
- `portability/srp_history_v1/` **não substitui** o anterior: acrescenta 9 classes de trajetória flop→turn e regras particulares de turn/river, com fonte OpenPPL única e gerador offline.
- Versões históricas e novos módulos devem permanecer reprodutíveis. Consultar e atualizar este arquivo juntamente com `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md`, `CHANGELOG.md`, `RELEASE_MANIFEST.md`, `PORTABILITY_CONTRACT.md` e `README.md` a cada checkpoint importante.

## Critérios práticos de conclusão

1. **Cobertura:** nenhum estado do domínio anunciado sem regra de decisão e sizing aplicável; nós desconhecidos identificados e tratados explicitamente, sem fallback silencioso do OH.
2. **Histórico fiel:** eventos anteriores da mão, tipos de pote e ações do Hero/vilão coerentes inclusive em reavaliações e trocas de street; distinguir desconhecido de falso.
3. **Portabilidade:** fonte de ação em OpenPPL, não duplicação Python; confirmar símbolos e ação final no OH-alvo em replay desconectado de apostas.
4. **Qualidade:** medir erros graves de estratégia, consistência de ranges, adaptação a posição/stack/rake/sizing, revisão contra charts compatíveis, testes com diversas classes de oponente e amostras reais simuladas/observadas, sem alegar solução ótima.
5. **Entrega:** funcionamento de ponta a ponta em todo domínio alvo, documentação e regressão, rollback e logging — não simplesmente milhares de linhas OpenPPL.

## Sequência imediata

**HIST-1 (este checkpoint):** 3 estados exclusivos do flop × 3 do turn, 9 trajetórias, regras específicas, guardas para não classificar raise como c-bet, 18 testes. **HIST-2:** captura canônica de ações intra-street e posições de agressor/caller, bet-raise/call e check-raise. **HIST-3:** board texture/runout, SPR e sizings sobre essas linhas. **HIST-4:** 3bet/4bet/multiway/limped, além de perfis. **OH runtime:** validar paralelamente sem impedir a autoria dos módulos DRAFT, mas impedir qualquer alegação de bot pronto antes de um replay de ponta a ponta.

## G3-HIST-v2 — atualização do roadmap vivo (20/11/2026)
- **Entregue em DRAFT:** 6 famílias de histórico em flop e turn: B=bet-call, C=check-through, X=call, R=raise sobre bet, H=check-raise e M=bet→raise→call. **36 trajetórias** para o river, 70 helpers e 75 regras pós-flop, todas OpenPPL. Regressão preserva os 9 caminhos HIST-v1.
- **Não confundir classificação de flags com reconstrução exata:** podem existir ações adicionais dentro da mesma street; no-match continua inseguro em OH. O próximo objetivo é HIST-2b: reconstrutor cronológico/estado persistente e identificação de pote antes de construir a multiplicação de contextos (board, SPR, sizes).
- **Qualidade > contagem:** milhares de ramos só são úteis quando alcançáveis, semanticamente corretos e conectados às decisões relevantes. Esta versão não implica GTO exata nem excelência estratégica demonstrada.

## HIST-v3 — histórico cronológico como dimensão primária (ADR-026)
- Modelo base: sequência ordenada de eventos `(street, actor, action)`, Hero IP/OOP, Hero PFR/caller. Inventário finito com até quatro raises por street: **484 palavras de dois rounds que chegam ao river**, sem all-in, stacks, sizing, multiway ou ação estratégica imputada. [Matriz](portability/srp_history_v3/HIST3_484_CHRONOLOGICAL_PATHS.csv).
- Os 36 caminhos antigos eram combinações de flags agregados e são insuficientes; [3 colisões](portability/srp_history_v3/HIST3_OBSERVABILITY.csv) provam que não é possível reconstruir todo o histórico sem memória/eventos adicionais. `Set user` em OpenPPL + `BotsLast*Action` é o primeiro bridge, ainda não validado no executável real.
- A leitura do DeepCrusher_R10 e dos artefatos R10d foi **referência de complexidade e proveniência**, não fonte para transplantar ranges/heurísticas. Os 331 contratos de validação pós-flop históricos e 1.271 funções/listas R10d não são diretamente números de trajétorias comparáveis.
- **Arquitetura final desejada:** classificação por histórico real + pot family + posição + board/runout + SPR + sizing/action legality + hand/draw + adversário. Ter milhares de caminhos somente quando eles correspondem a estados realmente possíveis e têm políticas distintas; criar cobertura rastreável e fallback controlado, não apenas cartesian products. A etapa atual mantém 75 regras de ação e 10 helpers novos em OpenPPL, sem alegar completude.

**Métrica da HIST-v3 (ADR-027):** das 484 sequências legais flop→turn, a fonte OPPL v3 classifica **100** somente sob modelo documental de memória perfeitamente capturada; **384** não entram no domínio (264 flop/120 turn). Esse indicador, mais a taxa de replay real sem fallback, passa a orientar a expansão funcional. O próximo módulo precisa aumentar cobertura observável e associar ações em estados estratégicos, não apenas adicionar helper sem consumidor.

## Contrato mínimo do produto final: SUPERAR DeepCrusher_R10d (20/11/2026)
A comparação é com o [artefato R10d exato](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt), não com um resumo. Seu inventário foi medido: 725 funções, 545 handlists, 6.021 WHEN, 1.561 comandos Set e 561 símbolos user_. O Heuristic6max mais recente, com 3bet HU, tem 88 funções, 187 handlists, 649 WHEN, 57 Set e 6 símbolos user_ próprios. **Há um gap substancial; não alegar completude/superioridade.** Completude é dominância funcional, não contagem bruta; melhorar além de R10d significa incluir todas as 14 famílias auditadas em [CAPABILITY_MATRIX.csv](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv) e extensão significativa como multiway 4–6 players.
- Executável mais recente em DRAFT: [preflop + SRP-HIST-v3 + 3bet HU](portability/p3bet_hu_v1/preflop_srp_and_3bet_hu_draft.oppl); 39 regras novas de 3bet HU e captura de intenção, não execução.
- Engenharia orientada por gargalos: história real de ações e classificação do pote → cobertura de famílias faltantes → política por board/SPR/oponente → validação prática → promoção. Não usar multiplicações cartesianas de cenários como se fossem decisões.
- Release bloqueado até `PROMOTION_GATE.json` com evidência real, verificação de histórico/fallback/legalidade e cobertura comparativa. G2-a segue HOLD para alterações estratégicas, mas adições em novas famílias são DRAFT sob revisão.

## SRP 3-way e evolução do mínimo R10d
- Adicionado [módulo p3way_srp_v1](portability/p3way_srp_v1/README.md): 31 novas ações pós-flop para Hero PFR ou caller VS_OPEN, 33 comandos `Set` derivados da estratégia original, nativos de verificação do call/raise.
- O arquivo combinado [preflop_srp_3bet_3way_draft.oppl](portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl) soma 729 WHEN, 92 funções, 187 listas, 90 registros Set, 7 símbolos user_. **Ainda muito inferior em amplitude ao R10d**; a meta não pode ser substituída por mais 31 regras superficiais.
- Ponto de decisão: próximo aumento de abrangência deve resolver estados relevantes ausentes (multiway que vira HU, potes 3bet multiway e 4–6 players, limp/iso e 4bet), não inflar o grafo de históricos sem políticas. Avaliação futura exige ação final OpenHoldem e cobertura de cenários reais.

## ADR-031: integridade de ações acima da contagem de nós
Corrigida falha estratégica em ambas as novas famílias: HaveNuts enfrentando overbet podia atingir Fold residual. Quatro ramos flops/turns agora garantem CALL quando não aplica raise. Último integrado = 733 WHEN, 74 ações 3bet HU+SRP 3way. A lacuna para R10d continua grande; priorizar correção de escolhas e mais famílias reais, não inflação artificial de árvores.

## Expansão de potes e transições — ADR-032/033 (20/11/2026)
- Mais 74 decisões nativas OpenPPL cobrem potes com 4–6 jogadores ativos e a conversão 3–6way→HU; os estados preservam a quantidade ORIGINAL de oponentes no flop. Não contar automaticamente 484 trajetórias históricas como 484 decisões.
- Mais 33 decisões e 2 Check FORCE cobrem somente BB versus single-limp; a família limp/iso continua incompleta.
- Fonte integrada atual: [preflop_multiway_limp_bb_draft.oppl](portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl). Métricas 899 WHEN/106 f$/187 listas/92 Set/9 user_; **14 capacidades R10d ainda sem aprovação**. P1: quedas intermediárias, potes com limpers e isolation, multiway 3bet; após isso SPR, board/runout, perfis, multi-street e OH real.

## Implementação ativa de histórico de participantes e origem de pote (20/11/2026)
- SRP com 4–6 jogadores que perdeu parcialmente os adversários: 53 topologias cronológicas e 41 regras; classificações distinguem quando a redução ocorreu (flop/turn/river).
- BB pós-option CHECK contra 2–5 limpers: sete origens SB/Other, 39 ações posteriores, e verificação por `BotCheckedPreflop`; ainda **não** cobre iso.
- 3bet multiway: 117 topologias, 43 ações diferenciadas por agressor da 3bet vs RFI que pagou uma 3bet. Nenhum desses contextos é projetado para cair em SRP HU ou limp BB.
- O arquivo OpenPPL integrado contém 1.460 WHEN/136 funções/187 listas/99 Set/16 user_, sem alteração de ranges. **Não equivale a superar o R10d**: precisamos de histórico completo intra-street, limp iso/coldcall, 4bet/5bet, board/runout, SPR, perfis, stacks e testes da ação final em OpenHoldem real.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## ISO-1 — pot-family isolamento, sem mudança de baseline
- Cinco intenções preflop ISO em CO/BTN com contagem explícita de limpers e pot, **não** derivadas de uma interpretação ambígua de `RFI` ou `VS_OPEN`; listas RFI/VS_OPEN/VS_3BET congeladas. Um marcador `Set user_H6_ISO*` somente registra intenção, requer `BotRaisedBeforeFlop` e ausência de nova 3bet para formar domínio posterior.
- Famílias: 120 topologias possíveis por street dentro do domínio, 41 decisões efetivas com sizing e thresholds por número de oponentes. Limitação crítica: ainda não há trilha confiável da ação final e os resultados são heurísticas não calibradas. Não tratar contagem estrutural como equivalência ao R10d; M04 segue PARTIAL, runtime G6 bloqueado.

## BLISO-2: origem de blind isolation e distinção contra BB CHECK
- Novo domínio pós-flop não significa pote limped: origens de ISO só são válidas depois de RaiseTo marcado e `BotRaisedBeforeFlop` efetivamente relatado, sem `BotCheckedPreflop` ou `BotCalledBeforeFlop`. 13 tags separados de RFI, 3bet, VS_OPEN, 5 tags ISO-1 e 7 BB-limp.
- 120 topologias monotônicas, 43 ações e três buckets de oponentes; no HU distingue Hero SB (fora de posição) de BB quando em última posição. Não assumir, contudo, que `Position = Last` prova sequência do agressor sem replay.
- **Precedência importante:** novo RaiseTo do BB deve vir antes da política anterior de Check, que continua ativa no domínio não isolado. G1/G6 e regra de no-match continuam bloqueadores operacionais.

## ISODEF-1 — resposta versus isolador: pote raised com limper anterior
- Não tratar como VS_OPEN: este último usa `Raises=1`, `Calls=0`, enquanto ISODEF-1 permite `Raises=1`, `Calls=1`, pote exato 7 BB e agressor CO (Hero BTN) ou BTN (Hero BB). Nenhum caller extra de raise no momento da decisão. Guardas de posição negam Hero simultaneamente no BTN e BB.
- Proveniência: Hero `Set user_H6_DEF_BTN3/BB3` apenas ao 3betar, ou `BTNC/BBC` ao pagar; pós-flop requer flags nativas `BotRaisedBeforeFlop` vs `BotCalledBeforeFlop`, `NumberOfRaisesBeforeFlop=1`, sem tags herdadas. `defense_policy.oppl` cria buckets de ação por 3bettor/caller e HU/2 adversários; 3way→HU é aceito.
- **Não inferir** que `Calls=1` prova quem limpou, que o marcador prova a ação final, ou que `None` no intérprete desativa `default.bot`; gate operacional continua bloqueado.

## Observabilidade OH-G1G6-1 como pré-requisito de completude
- A arquitetura mantém fonte única OpenPPL e Python restrito à auditoria fora de runtime. A nova camada de evidências não é estratégia de poker e não adiciona `WHEN`, `Set user`, handlists, ranges, decisões de sizing ou perfis.
- `Best action` (ação escolhida pela fórmula), `Action taken` (ação de autoplayer) e estado posterior aceito pela simulação offline são observações separadas; coincidência textual e SHA não bastam. Contrato de 10 cenários e checklist: [OH-G1G6-1](portability/oh_runtime_gate_v1/README.md).
- Exigir G1/G6 antes de estender squeeze, short/deep, 4bet/5bet ou políticas baseadas em contadores; liberar somente mediante observações reprodutíveis sem fallback inesperado. [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886) confirma apenas a infraestrutura de auditoria.

## OH-SRC1 — critério de autoria de guards e contratos nativos
- Para cada novo `WHEN`, exige-se proveniência de símbolos e precedência na engine OpenPPL, não implementação independente em Python. `Calls` é resultado de contagem/memória e não sinônimo absoluto de limp; `StillToAct` só deve reger a primeira órbita; `Set user_*` é flag da mão, não comando terminal.
- Auditar comparações em ponto flutuante antes de copiar guardas: `PotSize` corresponde a valor em blinds (efetivo, com desconto de side pot). A [auditoria OH-SRC1](portability/oh_source_audit_v1/README.md) encontrou 436 igualdades exatas, sem autorizar reescrita massiva. `source_first` e regressão das 1.920 regras herdadas continuam obrigatórios.
- Desenvolver por código-fonte aberto sem hash do executable local; reservar teste de instalação, last action e fallback para **G1/G6 de certificação**. [CI OH-SRC1](https://github.com/pmartins87/Heuristic6max/actions/runs/44864070437) validou somente contratos estáticos, sem EV/GTO/runtime comprovados.

## M08-RIVER4 — sensibilidade de valor ao runout adverso
O módulo [river four-flush](portability/river_fourflush_v1/README.md) trata explicitamente um erro conceitual de usar `f$SRPStrongMade` como valor independente do board. O novo `f$H6RiverFourFlushNoFlush` atua somente em SRP HU com origem nativa RFI/VS_OPEN-call, `OneCardFlushPossible`, `NOT FlushOnBoard`, `NOT HaveFlush`, `NOT HaveNuts`. As quatro ações são lidas do OpenPPL (Call/Call/Fold/Check), precedem a árvore river histórica e preservam-na para todos os demais contextos. Limiares 20%/10% são heurísticos provisórios, não EV calculado. M08 parcial; não confundir com prova de paridade real da engine.
