# DeepPoker V2 v0.3 — correções sistêmicas de risco e contexto (22/11/2026)

**Estado:** candidata CONTEXT_REVIEW, não indicada para jogar. Fonte [v0.3](DeepPoker_V2_Cash6max_v0_3_CONTEXT_REVIEW.oppl). V0.1 permanece REVOKED_FOR_PLAY; v0.2 preservada como base histórica. Sem solver próprio e sem execução real no OpenHoldem nesta rodada.

## Fontes efetivamente lidas

O Manual OpenPPL (2015) e o Manual OpenHoldem fornecidos pelo usuário em OpenHoldem e OPPL Manuais e Library.zip; e o C++ fornecido em repositorio_completo_openholdem.txt (em especial CSymbolEnginePokerval.cpp). Os manuais declaram: PotSize inclui apostas atuais; AmountToCall é o custo incremental em BB; NumberOfOpponentsAllin informa jogadores all-in; BotIsLastRaiser representa a iniciativa da street anterior. NutFullHouseOrFourOfAKind classifica a força relativa de FH e quadras, sem incorporar straight flush. Símbolos de força e de draws podem se sobrepor.

## Problemas concretos atacados na fonte v0.2

| Área | Erro de classe | Alteração efetiva na v0.3 |
|---|---|---|
| **SPR e compromisso** | PotSize aumenta com a própria aposta do vilão. Quanto maior a overbet, mais facilmente a regra de baixo SPR autorizava call | DP_LowSPR e DP_Commitment verificam o pote-base descontando AmountToCall; made hands continuam exigindo limite de preço |
| **Premium não-nuts** | Full house não-nuts e outras mãos fortes tinham calls incondicionais em flop/turn/river | Respostas graduadas por categoria/nut tier, preço, textura e HU/multiway; nuts continuam podendo pagar |
| **Draws** | Gutshot, OESD e nut draw compartilhavam limiares e agressividade; um inside nut straight draw pode ter apenas 4 outs | Distinção entre DP_NutDraw e DP_GoodDraw, calls por flush/OESD/gutshot e duplo gutshot, sem premium para simples gutshot |
| **Jogadores all-in** | Tentativas de bet/raise quando não havia adversários com stack para continuar apostando | Check sem preço quando todos estão all-in; raise pós-flop só se outro adversário puder continuar; seleção pré-flop de call/fold |
| **Agressão anterior** | Blefes de river podiam surgir mesmo após raise do adversário no flop ou turn | Exigência adicional de ausência desses raises nos ramos de missed-draw |
| **Small blind com limpers** | Tratamento de 3bet-or-fold podia impedir completamento barato com mãos jogáveis | Separação de limp pot de decisão versus open raise |
| **Condições redundantes** | Predicado repetido sobre projetos e check em quadra comunitária | Remoção dos ramos inacessíveis, mantendo a prioridade correta |

### Evidência matemática de maior impacto

Com pote original de 10 BB, aposta adversária de 100 BB e StackSize do Hero de 80 BB, o PotSize observado pode ser 110 BB. A antiga verificação de baixo SPR comparava 80 contra 1,5 × 110 e retornava TRUE. A nova comparação com o pote descontado da aposta usa 80 contra 1,5 × (110−100) = 15 e retorna FALSE. A aposta enorme **não pode criar por si só justificativa para pagar**.

No turn, com 46 cartas desconhecidas, um gutshot de quatro outs limpos tem cerca de 8,7% de chance direta; um OESD com oito outs, cerca de 17,4%; um flush draw com nove outs, cerca de 19,6%. A avaliação real também depende de outs contaminados, implied odds, fold equity e adversário — os limites da v0.3 são aproximações heurísticas, não percentuais publicados de GTO.

### Limites assumidos (sem alegações indevidas)

A fórmula ainda não reconstrói ranges adversários por histórico completo, não separa todas as árvores de SRP, 3bet/4bet, side pot e multiway e não tem evidência de EV. Os limites de call e sizing desta versão **não são resultados de solver** e continuam sujeitos a erros estratégicos. A nova proteção para estados com todos os adversários all-in depende da semântica dos contadores nativos OpenPPL descrita no manual. Não afirmar operação no executável apenas pela leitura do código-fonte.

**Próximo incremento de estratégia:** revisar as famílias de bet inicial, check-raise, turn barrel, river polarizado e ações all-in com classes de mão, blockers, tamanho e história, ao invés de reabrir ajustes numéricos marginais. Atualizar a mesma fonte de verdade e testar no OpenHoldem quando existir versão estrategicamente defensável. A execução do bot v0.3 ainda não é recomendada.


### Emenda de consistência (22/11/2026)
- **Nuts atuais no flop/turn:** depois de limitar calls de mãos não-nuts, constatou-se que o mesmo bloqueio poderia dobrar o próprio `HaveNuts` frente a uma overbet. A ordem foi corrigida: nuts atuais continuam por call antes do cap de mãos fortes inferiores. Isso não implica 100% de equity nas cartas futuras — risco de redraw continua uma decisão estratégica.
- **Double gutshot e inside nut draw:** a separação de nut draws tinha tornado invisíveis algumas mãos de oito outs e parte dos gutshots de quatro outs. Foram criados ramos específicos por classe e preço para que um draw de oito outs não seja confundido com um gutshot, nem um gutshot de nuts se torne premium apenas pela palavra “nut”.
