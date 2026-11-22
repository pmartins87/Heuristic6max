> **PORTABILIDADE V2 — ADR-050:** versão [DeepPoker Cash6max v0.1](v2/bot/DeepPoker_V2_Cash6max_v0_1.oppl) escrita para o modo OpenPPL nativo dos manuais OpenHoldem, com callbacks completos e ações de fallback explícitas. O usuário fará o primeiro teste direto; se houver parser ou ação incorreta, corrigir com log. Não exigir certificação formal antes de entregar versões experimentais. O contrato operacional V1 abaixo permanece histórico, não bloqueador desta estratégia de entrega.

> **PORTABILIDADE V2 — ADR-049:** [Plano Vivo](v2/PLAN.md) e [Política geral](v2/GENERAL_POLICY.md). Os dois spots OpenPPL seguem como smoke tests; a arquitetura deve servir a famílias estratégicas diversas, sem copiar ações short-stack do DeepCrusher. Pesquisa F1/F2 não depende do OH instalado, mas **qualquer promoção operacional** exige parser/ação final/legibilidade do histórico comprovados. O texto abaixo contém contrato e histórico prévio.

> **PORTABILIDADE V2 — ADR-048:** [piloto source-driven](v2/pilot_01/README.md) passou 20 testes Python com modelo simbólico restrito, **não** parser OH. [Gate obrigatório de replay real](v2/pilot_01/OH_OFFLINE_EVIDENCE_GATE.md): histórico desde RFI, user_ por mão, stack do BB, tamanho de aposta e Best action vs Action taken. **F3 OH_PENDING, F4–F5 bloqueados.** Abaixo, contrato histórico de portabilidade V1 ainda válido no que couber.

# Heuristic6max — contrato de portabilidade obrigatória OpenPPL (ADR-016)

**2026-11-20 · Gate PORT-0 iniciado; NÃO operacional.** Contrato transversal ao roadmap; preserva G0/G1/G2 e não inicia antecipadamente a integração G6.

## Objetivo e recomendação de arquitetura

Não manter duas implementações independentes de uma decisão. **Cada regra que decide ação no runtime deve nascer em um subconjunto explícito da linguagem OpenPPL, com equivalência de semântica verificável.** O Python que simula essas regras lê o MESMO texto OpenPPL; não reimplementa a estratégia com estruturas arbitrárias.

A exigência de equivalência **linha a linha literal Python ⇔ OpenPPL** não é implementável como promessa universal: a sintaxe é diferente, Python tem estruturas que OpenPPL não oferece, e OpenHoldem adiciona semânticas próprias de runtime. A garantia útil é: **cada ramo de decisão tem uma origem OpenPPL audível e a mesma regra é interpretada em Python com testes de paridade**. Sempre que a paridade não puder ser demonstrada, o ramo fica sem promoção para execução.

Não limitar bibliotecas de **auditoria, Monte Carlo, importação de charts, testes, exportação e reconstrução de histórico offline**. Elas não são lógica de decisão no runtime e não precisam virar OpenPPL. Limitar **apenas o núcleo de regras e seus predicados/ações**.

## Extraído do manual local efetivamente consultado

Fonte: anexo `OpenHoldem e OPPL Manuais e Library.zip` → `OpenPPL Manual.pdf` e `OpenPPL_Library_Integrated.txt` (documentação de aproximadamente 2015; **versão executável do OpenHoldem alvo não verificada**). O manual suporta:
- Seções `##f$preflop##`, `##f$flop##` etc., regras `WHEN condição ação FORCE`, `RETURN`, `RaiseTo`, `RaiseBy`, `Call`, `Check`, `Fold`.
- Execução de condições **de cima para baixo**: a primeira correspondente prevalece.
- Um único nível de condições `WHEN` abertas; múltiplos níveis de aninhamento **não** são suportados.
- `hand$AA`, `hand$AQSuited` e outras expressões de mão, handlists `##list...##` e funções `f$...`.
- `Random` inteiro em [0,99] versus `random` OH-script real em [0,1); não confundir.
- `Set user...` e memória OH `me_st_...` têm limitações de persistência/reinicialização. O manual alerta que símbolos baseados em histórico e scraping podem ficar indefinidos ou inconsistentes.
- O OpenPPL pode adaptar uma aposta ilegal ou usar uma **ação substituta**, inclusive Call/Check/Fold. Isso **não** é o mesmo que a falha explícita `None` prevista pelo nosso contrato Python.

## Regras mandatórias a partir de agora

1. **Fonte de verdade da lógica executável:** texto OpenPPL restrito, versionado, ou representação declarativa que gere OpenPPL e simulador a partir da MESMA fonte; nunca dois algoritmos com decisões independentes.
2. **White-list inicial:** `WHEN`, `AND`, `=`, `InButton`, `Raises`, `Calls`, `hand$AA`/`hand$KK`, `RaiseTo 2.5 FORCE`, somente em **prova demonstrativa BTN RFI**. Novos símbolos/operações requerem evidência de suporte real, adaptação do intérprete e teste de paridade.
3. **Bloqueados no runtime sem ponte de paridade:** `hashlib/sha256` como sorteio estável, `dict`, loops, classes/Enum, algoritmos de equidade, estado privado não observável, `source_quality=HIGH` sem predicado equivalente em OH, 4bet sem controle de legalidade equivalente.
4. **Misturas:** sem `Random` ingênuo em múltiplos ciclos de leitura. A seleção de ação deve permanecer estável no mesmo nó/mão. Não promover misturas antes de mecanismo de memória e resete verificáveis no OpenHoldem alvo.
5. **Fallback:** Python `None` NÃO equivale a `WHEN Others Fold/Check` e o OpenHoldem pode aplicar ações de backup. Sem mapeamento de falha explícita, **bloquear a promoção operacional** do ramo.
6. **Escopo mínimo do gate de paridade:** mesmo predicado/ação/prioridade, sizing **RaiseTo vs RaiseBy**, unidades (BB), guarda de posição/stacks/ação anterior, legalidade, estado do scraping, histórico estável, repetidas avaliações e resultado final do OpenHoldem (não só parser estático).
7. **CI:** para cada novo módulo de decisões, exigir regras OPPL, intérprete de testes do subconjunto, casos positivos/negativos, reprovação de construções não mapeadas. Arquivos anteriores permanecem históricos e **não são declarados portáveis retroativamente**.
8. **Gate real de G6:** testes do comportamento no OpenHoldem de versão especificada, com snapshots e replays de TESTE sem apostas, comparação da ação final, e fallback/rollback. O piloto atual **não foi compilado nem executado no OpenHoldem**.

## Prova implementada neste checkpoint

`portability/portable_rfi_probe.oppl` possui **duas regras nativas de OpenPPL** para BTN RFI puro AA/KK, 2,5 BB, só como prova de conceito. `portability/oppl_probe.py` é apenas intérprete de testes desse subconjunto. `portability/test_oppl_probe.py` cobre **3.042 estados de mão/posição/contadores** e recusa funcionalidades não permitidas. Falta guarda real de mesa 6-max, stack efetivo, scrape, validação de histórico, ação final, e a semântica de **não correspondência** não é idêntica ao OpenHoldem. **Não carregar como perfil executável.**

## Critérios condicionais

- **PORT-0** (contrato e piloto estático): aprovar somente após CI; não equivale a bot.
- **PORT-1** (1 nó completo sem mix): somente após identificação dos símbolos OH e paridade de ações em casos normais/limite.
- **PORT-2** (misturas e histórico): somente com persistência aleatória comprovada e estado confiável.
- **PORT-3 / G6**: OpenHoldem real, replays, legalidade, fail-closed, regressão paritária; bloqueado até G2 estratégico e G1 exigirem avanço.

A cada nova implementação estratégica, consultar este contrato e atualizar `DECISIONS.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `HANDOFF.md`, `README.md`, `CHANGELOG.md`, `RELEASE_MANIFEST.md`. **Não modificar os ranges RFI/VS_OPEN/VS_3BET neste checkpoint.**

## PORT-1 parcial — evidência de compatibilidade estática (ADR-017, 20/11/2026)
- [portability/port1/README.md](portability/port1/README.md) apresenta o subconjunto LJ RFI com 43 pure raises, 125 pure folds, KJo 40% raise não implementado; 15 testes e fonte única OpenPPL.
- Guardas sob verificação: IsPreflop, nplayersdealt=6, InUTG, Raises, Calls, StillToAct, PotSize, AmountToCall, StackUnknown, StackSize, MinOpponentStackSize e MaxOpponentStackSize. A documentação fornecida descreve esses símbolos, mas seus valores no OH-alvo não foram verificados.
- **PORT-1 continua ABERTO.** Interpretador Python None em regra ausente não assegura fallback seguro no OpenHoldem; ainda exige mistura KJo estável 40/60, OH real, legalidade, sizing, snapshots e replays de teste.

## PORT-2 — atualização específica da exigência de mistura (ADR-018)
- A documentação local OpenPPL/OH confirma `randomhand` no intervalo [0,1), gerado uma vez por mão. **Preferir `randomhand` a `Random` por avaliação** para mistura estável no mesmo nó (sem afirmar independência entre múltiplos nós).
- [portability/port2/](portability/port2/) é a prova estática de 169 mãos LJ; KJo fica em lista exclusiva com dois ramos complementares `< 0.40`/ `>= 0.40`, ordenados, e o interpretador recebe `randomhand` como observação de teste.
- **Novo critério PORT-2a (satisfeito estaticamente):** expressar KJo misto sem hash nem memória própria, preservar 169 classes, não duplicar lógica e cobrir testes de limiar e reavaliações.
- **Critério PORT-2b (ABERTO):** comprovar no executável OH-alvo os símbolos, estabilidade/mudança entre mãos, final action, falsos positivos na detecção, fallback, legalidade de RaiseTo e ausência de desvio em replay sem apostas. Não declarar PORT-2 concluído operacionalmente.
- Os trechos históricos de PORT-1 que citam KJo bloqueado continuam válidos para o ARTEFATO PORT-1, mas foram superados na prova PORT-2. Nenhum range mudou.

## PORT-3 / RPL-0 — condições de observação verificáveis (ADR-019)
- Não aceitar teste do Python como evidência do OpenHoldem. Cada amostra OH futura deve incluir `openholdem_version`, SHA da mesma fonte PORT-2, identificador da mão/sessão e avaliações, valores de guardas + `randomhand`, decisão da fórmula e **ação final tomada**, tamanho exato de RaiseTo, arquivo local e SHA256.
- [Auditor offline](portability/port3/README.md) detecta drift da fórmula, alteração do número aleatório dentro da mão, no-match/fallback, discrepâncias de ação e sizing, prova ausente ou adulterada. **`READY_FOR_MANUAL_REVIEW` exige inspeção humana da evidência e não aprova G6**.
- **PORT-3a PREPARADO:** 27 testes sintéticos, 5 STATIC_ONLY, 1 BLOCKED_NO_MATCH. **PORT-3b BLOQUEADO:** sem OH-alvo, sem frame real, sem observação de ação final.
- Não redistribuir logs/frames com dados sensíveis nem conectar autoplayer a mesas reais para experimentar. Preservar G1/G2/G6, snapshots e ranges sem alterações.

## RFI-MVP — implementar decisões com uma só fonte OpenPPL (ADR-020)
- O requisito OpenPPL-first agora cobre **cinco posições RFI**, 845 pares e 5 mixes (inclui SB limp). [Fonte, guardas e validações](portability/rfi_mvp/README.md).
- **Python autorizado exclusivamente para ferramentas offline** de compilação, inspeção, teste e relatório; a fonte da ação final simulada é o arquivo `rfi_6max_mvp.oppl`.
- Estratégia continua DRAFT: o módulo OPPL não define fallback seguro em cenários fora de domínio; um `default.bot` pode agir onde nenhuma regra encontra correspondência. OPPL completo + replays de OH antes de uso.
- Metas de qualidade pragmáticas: validade de sintaxe simbólica/ações, cobertura de linhas, comportamento estável das misturas, não regressão; **não exigir prova científica de GTO/EV para continuar a autoria DRAFT**.

## VS_OPEN-MVP — primeira árvore de resposta a open (ADR-021)
- O requisito OpenPPL-first cobre agora 5 posições RFI (845 classes) + 15 VS_OPEN (2.535 classes). A fonte `preflop_rfi_vsopen_draft.oppl` gera uma única função `f$preflop`; RFI e VS_OPEN não competem porque `Raises=0` versus `Raises=1`.
- [Código e 19 testes](portability/vs_open_mvp/README.md) conferem o próprio OPPL contra ranges v0.6.1 **sem segunda política Python**. Guardas exigem `FirstRaiserPosition`, `LastRaiserPosition`, `Calls=0`, pote, sizing e stack; todos são apenas candidatos a símbolos para validar no executável-alvo.
- Mixes 3BET/CALL, 3BET/FOLD e CALL/FOLD preservam `randomhand`, fonte e prioridades. **Nenhum OHReplay real, nenhum fail-closed garantido.** Próxima etapa VS_3BET de mesma base, e teste OH antes de promover a bot. Não usar este rascunho para apostar.

## VS_3BET-MVP — aplicação prática da fonte única (ADR-020)
- [portability/vs_3bet_mvp/](portability/vs_3bet_mvp/): decisões de VS_3BET nascem da fonte declarativa/handlists OpenPPL, interpretadas em teste Python a partir do **mesmo arquivo**, com 23 novos testes de regressão e sem duplicar política em runtime.
- `Raises` do OpenPPL conta raises **adversários** (1 após RFI do Hero + uma 3bet), não raises totais (2); para diferenciar `VS_3BET` de `VS_OPEN`, exigir `BotRaisedBeforeFlop`, `RaisesSinceLastPlay=1`, `FirstRaiserPosition=Hero` e `LastRaiserPosition=vilão`.
- Guardar stack anterior à ação RFI com `StackSizeAtBeginningOfCurrentRound`. Comparações da classe e do sizing usam correspondência exata da v0.6.1. Sem regra para nós inalcançáveis, sem `WHEN Others` nem fallback inventado.
- Esses símbolos de histórico **não foram comprovados** na compilação e no runtime da versão OpenHoldem-alvo. A aprovação estática do código não substitui gate de ação final/backup; arquivo combinado (277 regras) ainda é DRAFT e não deve ser executado em jogos reais.

## PORT G3 — pós-flop SRP HU (20/11/2026)
- A fonte de decisão continua sendo **OpenPPL puro**, não uma estratégia Python depois traduzida: [portability/srp_hu_mvp/](portability/srp_hu_mvp/) implementa cinco funções auxiliares e 33 regras (flop/turn/river). O interpretador somente LÊ as regras e usa símbolos de teste.
- Whitelist ampliada para `HaveNuts`, `HaveTwoPair`, `HaveTopPair`, `HaveBestKicker`, `HaveFlushDraw`, `HaveNutFlushDraw`, `NumberOfRaisesBeforeFlop`, `OpponentsOnFlop`, `BotRaisedBeforeFlop`, `BotCalledBeforeFlop`, `Position = Last`, `BetThirdPot`, `BetHalfPot`, `BetTwoThirdPot`, `RaiseHalfPot`, etc.; documentação do manual anexado verificada, **sem executável alvo verificado**.
- Regras misturadas usam `randomhand` fixo por mão; não criar RNG Python paralelo. Arquivo combinado preserva byte a byte as funções anteriores.
- **Bloqueio G3 importante:** a combinação atual de símbolos não garante exclusão de todos os potes com limper/isolamento; além disso no-match pode cair em fallback OH. Não anunciar como regra SRP estritamente identificada nem promover a execução sem replay offline e tratamento de estado ambíguo.

## G3-HIST-v1 — escala por histórico sem lógica duplicada em Python
- [Overlay OpenPPL](portability/srp_history_v1/history_overlay.oppl) registra os estados B (bot bet/call), C (check-through), X (bot call) em flop e turn, gerando nove caminhos compostos; o Python apenas mescla as fontes OpenPPL e interpreta os mesmos `WHEN` de teste.
- Flags OH como `NoVillainBetOrRaisedOnFlop/Turn` são exigidos para não confundir bet-call do bot com raise a aposta adversária. Operações incoerentes/raises múltiplos ficam **UNCLASSIFIED** no simulador, não marcadas como Fold.
- Nenhum runtime OH foi testado; contadores por órbita podem perder histórico, e `None` continua diferente do default.bot. Gate PORT/G6 segue bloqueado. O grafo deve crescer com tipos de linha, board, SPR e oponente, preservando controle de legalidade e integridade das ações.

## G3-HIST-v2 — expansão por ramos cronológicos (ADR-025)
- [Overlay OpenPPL](portability/srp_history_v2/advanced_history_overlay.oppl) introduz seis predicados próprios: raise sobre bet adversária pago, check-raise pago, bet→raise→call no flop e turn. Um montador de estrutura gera 36 helpers a partir desses predicados nativos; **não há heurística independente escrita em Python**.
- HIST-v1 permanece importado e preservado, com regressão de equivalência dos 9 pares B/C/X. As novas 17 regras são candidatas de história, não solver.
- **Bloqueios inalterados:** símbolos OH precisam ser observados em replay real (inclusive contadores por órbita), ações podem ser substituídas no runtime, e retorno None da simulação não impede fallback. Não promover para uso operacional.

## HIST-v3 — correção da biblioteca native OpenPPL e memória observacional (ADR-026)
- [Fonte](portability/srp_history_v3/README.md) faz auditoria de 11 sequências legais completas por street, 484 combinações flop/turn por posição e papel PF, 3 aliases dos resumos de flags. Não confundir contagem estrutural com política jogável.
- Fonte pública `OpenPPL_Library_Betting_Action_Symbols.ohf`: `OpponentCalledOnFlop/Turn` exige `NoVillainBetOrRaised...`; portanto R/H de HIST-v2 **não podiam depender desse símbolo** após aposta inicial do vilão. A v3 consulta sinais de raise e continuidade apenas na street seguinte.
- Registrar linha IP ambígua com `BotsLastFlopAction/TurnAction` e `Set user_H3...` apenas após evento anterior observado, jamais pelo sorteio futuro de ação. `Set` não equivale a prova da ação executada e flags podem resetar; sem captura válida, bloquear roteamento `BetRaisedCall` IP. A ação final OH/fallback ainda precisa ser verificada.
- Continuar a usar somente OpenPPL como fonte das decisões; intérprete em Python lê a mesma sintaxe, sem policy paralela. Preservar snapshots antigos e roadmap G1/G2/G6.

**ADR-027: medição compulsória de cobertura real por ramo.** Os 484 históricos de gramática do HIST-v3 possuem somente 100 admissões de domínio em **simulação hipotética da biblioteca OPPL**, 384 lacunas. Admissão não é ação final do OpenHoldem; não usar o número de caminhos gerados como prova de cobertura estratégica. [Relatório reprodutível](portability/srp_history_v3/HIST3_ROUTING_COVERAGE.csv).

## P3BET-HU e novo gate superior R10d (ADR-028/029)
- Reutilizar a fonte `portability/p3bet_hu_v1/preflop_srp_and_3bet_hu_draft.oppl` como **único código de ação**: 39 novas regras para 3bet HU e duas famílias de `Set user` de origem extraídas de RaiseTo existente. `Set` registra **intenção**, nunca prova execução; exigir flags de Bot e street subsequente. Históricos contraditórios excluídos; nenhum fallback fake no Python.
- O limite de cobertura final é [benchmark R10d](benchmarks/r10d_floor/README.md), com **14 capacidades mandatórias**, incluindo multiway 4+, potes 4bet/limp/iso, histórico real, board/SPR e ação final OH. Um teste estático nunca prova atendimento. Não mudar estratégia preflop por desejo de superar contagem.
- **Atenção:** a fonte R10d inclui 1.561 comandos Set e centenas de símbolos, mas copiá-los sem rastrear origem poderia piorar a qualidade. Se a memória OH-alvo não suportar cronologia confiável, parar a expansão artificial, corrigir adaptador/observabilidade e reavaliar plataforma antes do uso.

## Multiway SRP 3 jogadores — guardas adicionais (ADR-030)
- O último .oppl integrado inclui 3way e postflop 3bet HU. O marcador `user_H6_VSOpenCallIntent` nasce exclusivamente de condições preflop `Call FORCE` VS_OPEN; a ação REAL deve também ser confirmada por `BotCalledBeforeFlop` e ausência de raise de Hero. `Set` não é prova de click legal.
- Escopo restrito: exatamente 2 oponentes desde flop, 2 ainda ativos, RFI do Hero ou VS_OPEN Call, sem all-in. Nunca reinterpretar este módulo como SRP 4+ ou 3way que perdeu um oponente; há risco de default.bot quando não corresponde.
- Fonte OpenPPL única; Python lê e verifica, mas não decide à parte. Não promover até OHReplay real e controle de ação final/backup. M05 do piso R10d apenas PARTIAL.

## ADR-031 — não deixar nuts cair em folds de preço
Após a decisão RaiseHalfPot opcional com `HaveNuts`, exigir CALL prioritário sem teto de pot odds reservado a mãos mais fracas, antes do FOLD residual. Testar a mesma fonte OpenPPL com adversarial overbet; caso real/ação final OH permanece sem comprovação.

## ADR-032/033 — Topologia multiway e check de BB versus limp
- [Multiway-v2](portability/multiway_v2/) exige OpponentsOnFlop=3/4/5 e OpponentsLeft igual para potes com 4–6 jogadores, ou OpponentsOnFlop=2..5 e OpponentsLeft=1 para transição HU. **Não** extrapolar para perdas intermediárias não implementadas.
- [LIMP-BB-v1](portability/limped_bb_v1/) exige InBigBlind, Calls=1, Raises=0, StillToAct=0, AmountToCall=0 e PotSize 2/2.5 para Check FORCE. A fonte documental `OpenPPL_Library_Integrated.txt` usa **BotCheckedPreflop**; testar na instalação OpenHoldem antes de confiar no símbolo e no reset da memória.
- As duas fontes OpenPPL são interpretadas diretamente em testes Python. O no-match em Python não é fail-closed OpenHoldem; nunca inferir segurança operacional de CI. R10d gate não aprovado.

## NOVO: progressão multiway e origem do pote por street — ADR-032..035
- Contagem cronológica de participantes usa `OpponentsOnFlop`, `OpponentsOnTurn`, `OpponentsOnRiver` (entrantes por street) e `OpponentsLeft` (restantes agora); as combinações válidas são enumeradas e não provam sequência de apostas.
- BB contra 2–5 limpers: origem exclusiva por `Calls`, pote e `InBigBlind`; a ação de CHECK é confirmada posteriormente por `BotCheckedPreflop`. Potes 3bet multiway exigem marcador de 3bet + `BotRaisedBeforeFlop` ou RFI + `BotCalledBeforeFlop` com `NumberOfRaisesBeforeFlop=1`.
- +123 regras flop/turn/river e +7 contextos BB-CHECK em arquivo integrado. Testes Python interpretam o MESMO OpenPPL, e todos os WHEN ancestrais ficam preservados na ordem original.
- Não existe equivalência demonstrada para o executável OH instalado: símbolos, memória `user_`, no-match/default.bot, sizing legal e ação final precisam de replay antes de uso. Nenhum gate operacional aprovado.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## PORT ISO-1 — intenção de isolamento e prioridade da ação final
- `user_H6_ISOCO1/CO2/BTN1/BTN2/BTN3` registra **intenção** no momento de `RaiseTo`; não é prova de raise executado. Pós-flop também exige `BotRaisedBeforeFlop`, `NOT BotCalledBeforeFlop`, `NumberOfRaisesBeforeFlop=0`, ausência de RFI/3bet/limp BB concorrente e topologia de jogadores possível. A identidade do preço e a normalização de `PotSize` ainda são hipótese do interpretador da própria fonte OpenPPL.
- 13 novos testes estáticos propostos; runtime, fallback, repeat-scrape, reset de `Set`, tamanho efetivo de RaiseTo e legalidade da ação só podem ser aprovados por replay desconectado de apostas no OpenHoldem-alvo. Não executar o DRAFT em cash.

## BLISO-2 — contrato de ação pré-flop BB versus SB
- Os 13 marcadores `user_H6_BISO*` são intenções registradas na mesma condição de `RaiseTo`; não comprovam que o raise foi executado. O módulo se recusa a reconhecer pote isolado quando `BotCheckedPreflop` é verdadeiro. A ordem integra novas ações de BB antes do Check herdado somente para a handlist específica, conservando o Check e os marcadores do BB não-isolador.
- A geometria `Calls/PotSize` com SB completado e `NumberOfRaisesBeforeFlop=0` após raise do Hero permanece **a validar no OH real**; somente replay desconectado pode aprovar legalidade, sizing final, reset de memória e fallback. Intérprete Python é espelho da fonte OpenPPL, não estratégia independente.

## ISODEF-1 — protocolo de comprovação de defesa à isolation
- Duas entradas estritas na primeira decisão do Hero: BTN vs CO ou BB vs BTN após 1 limp, pote 7 BB, `Raises=1`, `Calls=1`, preço e posições exatos; `Set` imediatamente seguido pela mesma condição do `RaiseTo` ou `Call`. TAG de intenção não significa execução.
- Pós-flop exige confirmação de `BotRaisedBeforeFlop` *xor* `BotCalledBeforeFlop`, `NumberOfRaisesBeforeFlop=1`, exclusão das memórias ancestrais e contagens cronológicas de oponentes. Duplo indicador BTN+BB é rejeitado nos guardas pré-flop.
- Validar no OpenHoldem offline a semântica real de `Raises/Calls/StillToAct/FirstRaiserPosition/LastRaiserPosition`, sizing final, reset de memórias, contexto de player queue e no-match/fallback (inclusive `default.bot`), antes de autorizar qualquer release. Testes Python leem as mesmas fontes OpenPPL, não são prova da engine.

## OH-G1G6-1 — gate de evidências reais sem autopromoção
- A partir do ISODEF-1, qualquer aceitação exige **três planos separados**: (a) símbolo efetivamente observado no `f$debug` e histórico em múltiplas capturas; (b) decisão de fórmula registrada em `Best action`; (c) `Action taken` **mais** confirmação independente do processamento no simulador offline (aceitação e sizing final). `Best action` pode divergir de `Action taken` por fallback, conforme os manuais fornecidos.
- [OH-G1G6-1](portability/oh_runtime_gate_v1/README.md) verifica SHA-256 do integrado, identidade informada de exe e tablemap, pre/post frames .html+.bmp, debug text+png, log de uma decisão e estabilidade de `randomhand`. `READY_FOR_HUMAN_REVIEW` é um pacote coerente, mas não autentica origem nem ação final.
- **ManualMode:** símbolos e ação manual podem não reproduzir o histórico do autoplayer. **OHReplay:** frame estático não prova processamento real da aposta, nem `Set`/resets. Sem versão real instalada e logs, G1 ABERTO/G6 PENDENTE. G2-a HOLD para alterações de ranges; sem autorização de operação com dinheiro real.

## OH-SRC1 — prova de fonte x prova de instalação
- Fatos verificáveis independentemente da instalação: `Set user_*` prossegue após marcar a flag; C++ reseta no evento `UpdateOnHandreset`; `Calls`/raises usam mecanismos de histórico; `StillToAct` tem restrição de órbita; `PotSize` usa divisão por blind e correção de side pot; fallback não equivale a `None` Python.
- [análise OH-SRC1](portability/oh_source_audit_v1/README.md) quantifica **436 igualdades exatas `PotSize`** com teste automático de regressão; risco de limites reais não é licença para aumentar o domínio de seleção. Nenhuma prova de compatibilidade da build instalada foi reivindicada.
- **Construção sem hash privado permitida e prioritária**. Versionamento/hash de executável local pertencem somente à revisão de certificação operacional de um alvo específico, não são gate de autoria. **G1/G6 de release continuam pendentes**, G2-a HOLD, sem uso com apostas.

## M08-RIVER4 — precedência de fonte OpenPPL no river
`portability/river_fourflush_v1/river_policy.oppl` é a única origem das 4 ações de defesa contra river four-flush (sem flush/nuts do Hero), combinada de forma determinística ao ISODEF-1 imutável. `OneCardFlushPossible` e `FlushOnBoard` constam do manual OpenPPL fornecido; o Python apenas lê/testa as mesmas regras. O resultado não valida histórico nem sizing efetivamente aceito pelo executável. Nenhum range v0.6.1, G2-a HOLD, G1/G6 pendentes e 0/14 R10d foram relaxados.
