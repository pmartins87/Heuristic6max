# ADR-054 — DeepCrusher / CrusherTBP como fonte de arquitetura de histórico para cash 6-max

**Data:** 22/11/2026. **Escopo:** transplante seletivo de mecanismos de história e roteamento, **não de estratégia short stack**. Consultar [Plano Vivo](PLAN.md), [Registro Vivo de Decisões](DECISION_LEDGER.md), [DECISIONS.md](../DECISIONS.md) e [HISTORY_MODEL.md](HISTORY_MODEL.md) antes de nova alteração. Status desta etapa: *source reviewed, integration candidate*, nenhum OH runtime.

## Fontes lidas (arquivos reais)

1. **DeepCrusher R10d**: `pmartins87/DeepCrusher` / `artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt`, **blob Git** `9f9cba79cdb9dc4438895770cf61a450fb55d17c`. Leitura do blob real neste turno.
2. **CrusherTBP original** fornecido pelo usuário como `CrusherTBP(2).txt` (~505.030 caracteres / 12.744 linhas), incluindo `f$pot_*`, `f$Init_*`, callbacks `f$ini_function_on_new_round` e roteador `f$river_Call`. Também foi lido `DeepCrusher(1).txt`, ~973.462 caracteres.
3. **OpenPPL Manual.pdf** e **OpenHoldem Manual.pdf** fornecidos pelo usuário. O manual OpenPPL, seções *BettingAction Symbols* e *User-Defined Variables*, define `BotIsLastRaiser`, `BotRaisedBeforeFlop`, `BotCalledBeforeFlop`, `NoBettingOnFlop/Turn`, `OpponentCalledOnFlop/Turn`, `RaisesBeforeFlop` e contadores; `user_` dura uma mão e `Set` não prova execução; `me_st_` não reseta automaticamente.
4. **v0.4 V2**: [fonte atual](bot/DeepPoker_V2_Cash6max_v0_4_HISTORY_REVIEW.oppl), com 15 helpers históricos que **devem ser preservados e não duplicados**.

## Evidência direta do legacy e decisões de portabilidade

| Código legado observado | Mecanismo existente | Reutilizar? | Ajuste necessário |
|---|---|---|---|
| `f$pot_Limped`: `!RaisesBeforeFlop && !BotRaisedBeforeFlop` | Partição por origem de pote | **SIM, com escopo** | Aplicar após pré-flop. Antes de terminar o pré-flop essa expressão também pode descrever pote ainda unopened, não limped confirmado |
| `f$pot_SingleRaised` | Diferença raised vs limped | **SIM, reescrito** | Excluir verdadeiros reraises; distinguir Hero RFI, Hero ISO e raise inicial do vilão, sem atribuir ISO por mera ausência de raise |
| `f$pot_Reraised` | Candidatura a pote 3bet/4bet | **SIM, reescrito** | Em preflop `RaisesBeforeFlop && !didcallround_preflop` pode ser verdadeiro quando Hero apenas **enfrenta** um open e ainda não decidiu; não prova sozinho 3bet no histórico concluído. A V2 usa o evento de raise de ambos ou duas raises de oponentes |
| `f$Init_Hero`: `didbetsizeround_previousround || didraisround_previousround` | Iniciativa pela agressão da street anterior | **SIM, com mudança** | Uma bet anterior do Hero não prova que ele terminou como agressor (pode ter sido aumentado pelo oponente e pago). Preferir `BotIsLastRaiser`, definido pelo manual para o último agressor da street anterior |
| `f$Init_Villain`, `f$Init_Nobody` | Roteamento Hero / adversário / nenhum | **SIM, com domínio** | Em HU desde flop, separação segura por `BotIsLastRaiser` e `NoBettingOnFlop/Turn`. Em multiway, classificar apenas *not Hero*, sem afirmar identidade de qual adversário |
| `f$Init_GotRaised_Or_Isolated` | Perda de iniciativa / adversário aumentou | **CONCEITO SIM, expressão NÃO** | Legado combina `me_re_Initiativegotraised` e `me_st_Initiativegotraised_1`, que persistem sem reset automático. Não copiar estados opacos; usar `RaisesOnFlop/Turn` e `BotIsLastRaiser` com restrição explícita de confiabilidade |
| `f$river_Call`: dispatch por 4 classes de iniciativa, depois preço e força | Separação roteador → política | **SIM, arquitetura** | Não copiar `f$act_*` por percentuais ou `f$hand_*` de Spin&Go; criar helpers de origem/iniciativa e referenciá-los em política existente |
| `user_R10_HUSB_CalledProbeTurn` e `user_DC9R_HUBB_CalledTurn_AfterFlopXC` | História nominal entre streets | **SIM, padrão de marcação** | Só usar intenção `Set user_` combinada à confirmação nativa da ação final, conforme ADR-053 |
| `f$ini_function_on_new_round` com `me_st_Initiativegotraised_0` | Reset em mudança de street | **CONCEITO SIM; código NÃO** | `me_st_` não tem reset por mão garantido; a V2 precisa de prova de transições antes de adotar memória durável |
| `f$game_HUSB`, `f$game_HUBB`, `f$game_3w*` | Roteamento por posição/contagem | **ARQUITETURA SIM** | Contextos foram desenhados para Spin&Go; não representam todas as configurações 6-max e pot multiway→HU |
| `f$BetsizeFlopHeadsup`, `f$pot_Odds`, `f$stack_*` | Sizing/odds/stack | **NÃO PORTAR OS NÚMEROS** | Stacks 8–25BB, ICM/torneio/estrutura de pagamento e ranges não equivalem a cash 100–200BB |

## Reavaliação explícita de decisões anteriores

- **ADR-001/044:** SEM solver próprio e SEM pretensão de EV/GTO mensurado: **MANTIDAS**.
- **ADR-002 + protocolo ADR-053:** ler/atualizar GitHub, registrar contraditório antes de novas decisões: **MANTIDAS e reforçadas**.
- **ADR-049:** exemplos não são única prioridade: **MANTIDA**; esta integração é transversal.
- **ADR-050/051:** construir código sem burocracia acadêmica, mas **v0.1 pronta permanece revogada**.
- **ADR-052:** lógica objetiva de odds, mão/nuts/draws da v0.3 **MANTIDA**.
- **ADR-053:** usar históricos nativos com intenção `user_` seletiva e HU desde flop: **MANTIDA E REFINADA**. A nova evidência demonstra que o legado já tinha arquitetura reutilizável, **não** que devamos abandonar v0.4 ou confiar cegamente na R10d.

## Contraditório e decisão ADR-054

**A — copiar os helpers do CrusherTBP literal:** menor esforço imediato, mas migra inferências ambíguas, estados `me_st_` sem reset confiável e pressupostos HU/3-way em 25BB. **Não recomendar**.

**B — reescrever memória universal de todos os jogadores:** pode registrar cada ação/tamanho/autor, mas duplicaria parte da engine sem prova de captura estável; engenharia complexa e passível de descrever eventos que não ocorreram. **Não recomendar nesta fase**.

**C — integrar a arquitetura por composição, não copiar os predicados:** **RECOMENDADO E AUTORIZADO pelo pedido explícito “Continue”**. Reaproveitar roteadores de pot origin (limped, SRP, reraised), discriminar RFI/ISO e os quatro estados de iniciativa (Hero / adversário HU / nenhum / desconhecido), usar flags `user_` **somente para intenção** com prova posterior da execução. Preservar os 15 helpers e ações já existentes; conectar os novos símbolos às classificações de pote atuais, sem acrescentar apostas/limites por intuição.

**Condição de falha que altera a recomendação:** símbolos nativos de história inconsistentes na build OH efetiva do usuário, reset/atualização incorretos, identidade incorreta em multiway, ou necessidade concreta de tamanhos de apostas anteriores não presentes na engine. Só então justificar um registrador próprio com eventos e garantias de reset.

**Critério proporcional de conclusão desta etapa:** source único de cash 6-max com roteamento por pot family e iniciativa, tags origin RFI/ISO que não afirmem ação executada apenas pela flag, sem regressão óbvia de calls/bets; documentação viva sincronizada. **Não declarar certificação OH, GTO ou bot pronto para mesas.**

**Próxima etapa:** tornar a arquitetura de histórico efetivamente relevante para os ramos de defesa e valor por linha (triple barrel, delayed bet, check-raise, multiway), sem inventar que um isolador ou agressor anterior é necessariamente o último agressor do river.
