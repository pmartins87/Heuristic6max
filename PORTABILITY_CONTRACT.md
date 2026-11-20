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
