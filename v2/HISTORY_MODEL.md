# V2 — Modelo de histórico das ações e limite de confiança (ADR-053)

**Fonte atual:** [v0.5 CRUSHER_HISTORY_REUSE](bot/DeepPoker_V2_Cash6max_v0_5_CRUSHER_HISTORY_REUSE.oppl); v0.4 preservada [aqui](bot/DeepPoker_V2_Cash6max_v0_4_HISTORY_REVIEW.oppl). **Estado:** implementado em fórmula, **não observado em OpenHoldem real**, sem modelagem completa de ranges ou sizing passado. Consulte **antes de alterar o código** o [Plano Vivo](PLAN.md), [Registro Vivo de Decisões](DECISION_LEDGER.md) e [DECISIONS.md](../DECISIONS.md).

## 1. Por que esta arquitetura é necessária

Duas ações idênticas no river com a mesma mão/board/pote/tamanho podem representar ranges diferentes: uma aposta após flop e turn sem ação não é equivalente a uma aposta depois de flop bet-call + turn bet-call. O river **deve** saber o que aconteceu nas streets anteriores, mas reconhecer um símbolo como `BotRaisedOnFlop` não prova toda a sequência, quem chamou, nem o size da ação.

**Campos lógicos:** origem pré-flop (intenção e execução separadas), tipo de pote, quantos adversários viram flop, quantos estão na mão agora, agressão Hero vs adversário em flop/turn, check-through por street, raises adversários, calls do Hero, calls de adversário, iniciativa e custo atual. Os campos ausentes devem permanecer **UNKNOWN**, não virar falso histórico favorável.

## 2. Evidência primária consultada

| Símbolo | Comportamento fundamentado na fonte | Restrição |
|---|---|---|
| `BotRaisedBeforeFlop` | Hero apostou ou aumentou pré-flop, segundo `didraisround_preflop`/`didbetsizeround_preflop` | Pode ser ISO, 3bet etc.; **não prova RFI** |
| `user_DP_PF_RFIIntent` | `Set user_...` é definido antes da tentativa de abertura e se mantém na mão | Intenção de ação, não confirmação de ação tomada |
| `RaisesBeforeFlop` | Existiu raise de adversário pré-flop | Requer memória/histórico nativo confiável |
| `NoBettingOnFlop/Turn` | Nenhuma aposta/raise naquela street, **inclui Hero** | Check-through apenas após a street terminar |
| `NoVillainBetOrRaisedOnFlop/Turn` | Nenhum adversário apostou/raiseou, pela biblioteca `raisbits_[street]` | Não confundir com `NoBettingOn...` |
| `BotCalledOnFlop/Turn` | Hero deu call na street, com histórico de ação do autoplayer | Não informa sozinho o tamanho, nem quem apostou se multiway |
| `OpponentCalledOnFlop/Turn` | Biblioteca requer uma aposta/raise do Hero, sem check/call do Hero e sem bet adversária | Indicador forte de bet do Hero pago, não identidade se multiway |
| `BotRaisedOnFlop/Turn` | Hero apostou **ou** aumentou, não necessariamente c-bet | Só `BotRaisedOnFlop` não prova call de vilão |
| `RaisesOnFlop/Turn` | Raises do adversário, **não** apostas iniciais | Não conta todos os bets, nem identifica jogador |
| `OpponentsOnFlop` + `OpponentsLeft` | Número de adversários no flop e no momento | HU no river não prova que sempre foi HU |
| `AmountToCall` e `PotSize` | Custo atual e pote atual, incluindo apostas | Não reconstruir os sizes exatos de flop/turn a partir do pote atual |

Fontes: **OpenPPL Manual.pdf**, seções *BettingAction Symbols* e *User-Defined Variables*; **OpenHoldem Manual.pdf**, seção *History symbols do not work*; **OpenPPL_Library_Integrated.txt**, blocos `OpponentCalledOnFlop`, `OpponentCalledOnTurn`, `NoVillainBetOrRaisedOnFlop/Turn`, `UpdateMemorySymbolsAfterAutoplayerAction`.

**Aviso essencial:** os contadores OpenPPL precisam de atualização uma vez por órbita quando o estado está estável; a biblioteca executa atualização **após ação do autoplayer**. Sem isso, especialmente em uso passivo/manual, uma variável de histórico não necessariamente descreve a mão que se imagina. Isso é uma restrição da fonte, não um gate de certificação acadêmica.

## 3. Classificadores implementados (sem inventar identidade do vilão)

| Nome do helper | Como caracteriza o histórico | Limite |
|---|---|---|
| `DP_PF_OpenCandidate` | Zero raises/calls, posição e range RFI, sem ação anterior do Hero | Set apenas intenção pré-flop |
| `DP_PreflopRFI` | Intenção RFI + native Hero raised + ausência de raise adversário | Não inclui ISO/3bet; depende de histórico de raise |
| `DP_Hist_HUFromFlop` | OpponentsOnFlop=1 e OpponentsLeft=1 após flop | Exclui multiway→HU |
| `DP_Hist_FlopCheckedThrough` | Sem apostas na street flop após terminado | Nenhum sizings registrados |
| `DP_Hist_TurnCheckedThrough` | Sem apostas na street turn depois do turn | Idem |
| `DP_Hist_FlopVillainBetHeroCalled` | HU desde flop; Hero call; villain bet/raised, mas não houve raise adicional | Apenas linha geral de bet-call |
| `DP_Hist_TurnVillainBetHeroCalled` | HU desde flop; Hero call turn; bet/raise adversário sem raise extra | Sem identificação de bet size |
| `DP_Hist_FlopHeroBetVillainCalled` | HU desde flop; Hero bet/raised; o mesmo vilão pagou, sem bet adversária | Não prova iniciativa pré-flop |
| `DP_Hist_TurnHeroBetVillainCalled` | HU desde flop; Hero bet/raised turn; vilão pagou | Não provaria mesma pessoa em multiway |
| `DP_Hist_FacingTurnSecondBarrel` | Hero pagou aposta flop e enfrenta aposta turn no mesmo HU | Não assume necessariamente mesmo size |
| `DP_Hist_FacingTurnBetAfterOurFlopBetCalled` | Hero bet flop, vilão pagou e há aposta adversária para pagar no turn | **NÃO** afirmar donk; Hero pode ter dado check OOP no turn |
| `DP_Hist_FacingRiverThirdBarrel` | HU desde flop; Hero call flop, call turn, vilão aposta river, sem raises anteriores | Reconhece pressão; **ainda não calcula distribuição valor/blefe** |
| `DP_Hist_FacingRiverTurnRiverAfterPassiveFlop` | Flop check-through, Hero paga bet turn, vilão aposta river | Linha diferente de triplo barrel |
| `DP_Hist_FacingRiverFirstPostflopBet` | Flop e turn sem apostas; primeira agressão aparece no river, HU desde flop | Não é sempre bluff: pode ser trap/value tardio |
| `DP_Hist_FacingRiverAfterFlopBetTurnCheck` | Hero paga bet flop, turn checked-through, vilão aposta river | Não confundir com triplo barrel |
| `DP_Hist_OurDoubleBarrelWasCalled` | Hero aposta flop+turn e vilão paga ambas; HU desde flop | Histórico relevante para seleção de triple barrel futuro |
| `DP_Hist_FlopMutualRaising` | Hero apostou/raiseou e vilão também deu raise na mesma street, HU desde flop | **Não informa quem iniciou nem ordem exata; não é prova de check-raise do vilão** |

As classes são **não exaustivas** e algumas se sobrepõem quando há ações mais complexas. A ausência de uma classe **não** classifica automaticamente a mão como passiva.

## 4. Decisões que realmente mudam na v0.4

1. **Pré-flop:** antes de um `RaiseTo` first-in, `Set user_DP_PF_RFIIntent` sinaliza a origem, mas seu uso posterior exige confirmação por `BotRaisedBeforeFlop`. Antes o projeto confundia ISO sem raise de vilão com RFI.
2. **River em HU e linha passiva:** após checks-through em flop e turn e primeira aposta no river, um **par forte** em board não perigoso pode pagar sizings moderados que o ramo genérico anterior recusaria. A ação é heurística contextual, não um valor GTO publicado.
3. **River de bluff:** uma flag de intenção de apostar com draw só autoriza blefe se a engine confirmar que a aposta anterior do Hero ocorreu **e foi paga pelo adversário**. Isso impede simular uma linha fictícia quando o Set foi registrado, mas a ação não ocorreu ou o adversário já havia agredido.
4. **Outros ramos:** continuam herdados da v0.3 até nova revisão. Em particular, não afirmar que todos os calls de river agora considerem triplo barrel. O helper existe e deverá alimentar a próxima política de ranges, sem inventar fold universal antes das evidências.

## 5. Contraprovas e critérios para evolução

- **Contraexemplo de identidade:** três jogadores veem flop; um desiste no turn e Hero enfrenta river. Não é o mesmo HU desde flop; o helper não deve atribuir todo bet anterior ao vilão restante.
- **Contraexemplo de Set:** `Set user_...` executado antes de um Bet que não foi executado não prova história. Exigir símbolo da ação executada.
- **Contraexemplo de check:** `BotCheckedOnFlop` não equivale a flop checked-through; se vilão apostou depois do check, não se pode chamar de passivo.
- **Contraexemplo de first river bet:** um vilão pode ter slowplayado nuts em flop e turn; primeira aposta não é automaticamente blefe, por isso limitar o domínio da regra de par forte.
- **Contraexemplo de triplo barrel:** o adversário pode blefar três streets ou apostar fino por valor; sem frequências publicadas para mesma linha, **não** dobrar automaticamente todo top pair nem pagar qualquer size.
- **Contraexemplo de contadores:** uma falha no reset da mão ou na atualização pós-autoplayer pode alterar símbolos históricos, mesmo com fórmula correta.

**Próximo desenvolvimento:** atribuição segura de agressor e sequência com tamanhos por street quando o runtime fornecer dados, classificar check-raise e linhas multiway→HU sem inventar vilão, e aplicar `DP_Hist_...` a famílias inteiras de defesa e value em turn/river usando ranges adversários e blockers. Não construir um segundo sistema de memória nem configurar um solver sem nova evidência.


## 6. ADR-054 — reaproveitamento seletivo do CrusherTBP e DeepCrusher R10d

**Fontes concretas:** `CrusherTBP(2).txt`, `DeepCrusher(1).txt`, R10d blob `9f9cba79cdb9dc4438895770cf61a450fb55d17c`. [Auditoria rastreável](LEGACY_HISTORY_REUSE_20261122.md), [revisão das decisões](DECISION_LEDGER.md).

**Separar três eixos, nunca inferir um do outro:**

| Eixo | Helpers canônicos da v0.5 | Informação que NÃO se pode inferir |
|---|---|---|
| **Origem inicial** | `DP_Origin_HeroRFI`, `DP_Origin_HeroISO`, `DP_Origin_HeroRaiseUnclassified` | Que Hero ainda tem iniciativa; que um `Set user_` foi ação efetiva |
| **Família do pote concluído** | `DP_Pot_Limped`, `DP_Pot_SingleRaised`, `DP_Pot_Reraised`, `DP_Pot_Unknown` | Qual ação exata o vilão fez, nem número completo de agressões ao longo da mão |
| **Agressor da street anterior** | `DP_Init_Hero`, `DP_Init_NonHero`, `DP_Init_Nobody`, `DP_Init_OpponentHU`, `DP_Init_HeroLostAfterMutualRaiseHU` | Apostas do mesmo jogador em multiway; ordem detalhada de raise/check-raise |

**Proveniência RFI/ISO:** `f$DP_PF_ISOCandidate` usa `Raises=0`, `Calls>0` e as mesmas listas/condições que habilitam os raises de isolamento; antes das ações o código faz `Set user_DP_PF_ISOIntent`. No pós-flop, `BotRaisedBeforeFlop` confirma o raise; se ambas flags de intenção RFI e ISO forem true, **nenhuma** recebe atribuição. Caso o Hero tenha aberto e outro jogador dado 3bet, `DP_Origin_HeroRFI` permanece a origem, enquanto `DP_Pot_Reraised` é o pote atual: isso NÃO é contradição.

**Semântica de iniciativa:** no legacy `f$Init_Hero` usa se Hero apostou em qualquer momento da street anterior; isso pode perder informação quando outro adversário aumenta depois. A V2 usa `BotIsLastRaiser` *e* evidência de que a street anterior teve aposta/raise. A categoria `NonHero` é intencionalmente impessoal em multiway; `OpponentHU` só atribui ao vilão quando a mão é HU desde flop. `HeroLostAfterMutualRaiseHU` não presume quem fez check-raise, pois os contadores não fornecem ordem.

**Estratégia preservada:** o roteador `DP_ReraisedPot` agora delega ao classificador de pote e `DP_LastRaiser` à classe de iniciativa; o anterior `DP_PreflopRFI` remete à origem canônica. Não foram importados limites de size, stacks ou ranges da modalidade Spin&Go. Os 15 classificadores de história da v0.4 foram preservados e continuam delimitados a HU desde flop.

**Escopo não resolvido:** identidade e ordem de ações em potes que começam multiway, bet sizing histórico por street, confirmação runtime da atualização dos contadores no executável instalado e modelagem de ranges filtrados por agressão. Sem essas informações, `UNKNOWN` é preferível a uma narrativa falsa sobre a mão. **v0.5 permanece candidata.**
