# F0 case study — River paired four-flush / full house / ranges
**Data:** 21/11/2026. **Status:** AUDITORIA DE LÓGICA OBJETIVA CONCLUÍDA; AÇÃO ESTRATÉGICA ESPECÍFICA **NÃO APROVADA** (faltam histórico/ranges/preço/permissões). Subordinado a [../PLAN.md](../PLAN.md) e [../SOURCES.md](../SOURCES.md). Nenhum solver executado.

## 1. Estado físico, sem ambiguidade

Texas Hold'em 6-max cash, **apenas 2 jogadores no showdown** no exemplo; não há linha real pré-flop/flop/turn nem tamanho de aposta fornecidos.

- Board: **Q♠ J♠ T♠ 9♠ Q♥**.
- Hero: **Q♦ 9♦**.
- Melhor mão de cinco cartas do Hero: **Q♠ Q♥ Q♦ 9♠ 9♦ = full house de damas com noves (QQQ99)**.
- O board tem quatro espadas, mas **four-flush não altera a hierarquia da mão**. Qualquer flush não straight flush perde para QQQ99.

**Contraexemplos verificáveis (sem probabilidade/solver):**

| Vilão | Melhor mão vilão | Resultado contra QQQ99 |
|---|---|---|
| K♠ 2♣ | K♠ Q♠ J♠ T♠ 9♠ — straight flush ao K | **Hero perde** |
| 8♠ 2♣ | Q♠ J♠ T♠ 9♠ 8♠ — straight flush à Q | **Hero perde** |
| Q♣ J♥ | Q♠ Q♥ Q♣ J♠ J♥ — QQQJJ | **Hero perde** |
| Q♣ T♥ | Q♠ Q♥ Q♣ T♠ T♥ — QQQTT | **Hero perde** |
| Q♣ 9♥ | Q♠ Q♥ Q♣ 9♠ 9♥ — QQQ99 | **Empate** |
| 9♥ 9♣ | 9♠ 9♥ 9♣ Q♠ Q♥ — 999QQ | **Hero ganha** |
| A♠ 2♣ | A♠ Q♠ J♠ T♠ 9♠ — flush ao A | **Hero ganha** |
| 7♦ 2♣ | Não forma full house, flush ou straight flush | **Hero ganha** |

- O adversário pode formar straight flush se possuir **K♠ ou 8♠**, com outra carta compatível. Não são somente duas combinações de duas cartas.
- Para superar nosso full house com outro full house, precisa de **Q♣ junto de um J não bloqueado ou T não bloqueado**; Q♣9x apenas empata.
- **Quads não são alcançáveis pelo vilão neste exemplo específico** (as cartas de Hero/board bloqueiam pares de damas necessários, e as outras trincas disponíveis não viram quadra com somente duas hole cards). Isso não significa que quadras são impossíveis noutros four-flush paired boards.
- Frequência pré-flop plausível de K♠x, 8♠x ou Q♣Jx/Q♣Tx depende de posição, origem/ação de cada street e do range real do vilão. **Não substituir por frequência uniforme dos 45 cartões desconhecidos.**

## 2. Defeito comprovado do legado M08-RIVER4

Fonte real em `portability/river_fourflush_v1/river_policy.oppl`:
- `f$H6RiverFourFlushNoFlush` exige `OneCardFlushPossible AND NOT FlushOnBoard AND NOT HaveFlush AND NOT HaveNuts`; uma **mão full house não-nuts** é elegível (pode existir straight flush/full superior).
- Na fonte integrada, `##f$SRPStrongMade##` retorna TRUE para `HaveFullHouse`.
- Política de call com `f$SRPStrongMade` exige **AmountToCall <= 20% PotSize**; acima disso, `WHEN (f$H6RiverFourFlushNoFlush AND AmountToCall > 0) Fold FORCE` captura a mão. Não há revisão de range do vilão nesse ramo.
- Portanto, **a mesma fórmula pode foldar QQQ99 contra, por exemplo, bet de 50% pot**, independentemente de linha anterior e frequência de valor pior/blefes. Isto é **falha de especificação estratégica**, não prova de que o parser não executa o código corretamente.
- `NOT HaveNuts` significa apenas **não ser nuts**, não significa mão fraca/bluff-catcher frágil. `HaveFlush` ausente não equivale a `HaveFullHouse` ausente.

**Proibição para V2:** uma guarda genericamente baseada em board / ausência de flush / ausência de nuts e limiar de call **não pode roubar** linha de full house/quadra/straight flush ou outro valor extremamente alto sem uma política própria para aquela categoria e contexto.

## 3. O que fontes profissionais realmente sustentam (sem falsificar um solve do exemplo)

1. [GTO Wizard, *The Art of Bluff Catching*](https://blog.gtowizard.com/the-art-of-bluff-catching-2/): as decisões river dependem de **apostas de valor que ainda perdemos/ganhamos, blockers, bluffs e pot odds**. O artigo analisa outro runout e **não** fornece a ação exata para Q♠J♠T♠9♠Q♥/Q♦9♦.
2. [GTO Wizard, *Principles of River Play*](https://blog.gtowizard.com/principles-of-river-play/): valor relativo de blockers, ranges que chegam ao river e calibragem de defesa; não é solução da mão deste documento.
3. [GTO Wizard, *Maximizing Value on Monotone Flops*](https://blog.gtowizard.com/maximizing-value-on-monotone-flops/): no exemplo publicado de 4-flush **sem este board pareado**, há checks, bluffs e value bets; não justifica `check sempre` ou `fold acima de 20%`. Parte da análise publicada é 40bb deep; **não** copiar para 100bb paired river.

**Inferência/decisão de engenharia independente dos artigos:** uma mão QQQ99 é candidato muito forte a CALL em muitos ranges razoáveis e pode até ser value raise em linhas específicas. Fold só poderia ser aprovado em contexto concreto de vilão excepcionalmente polarizado e com valor mais forte suficientemente dominante, sem mãos piores/bluffs no preço oferecido. **Sem história/size não afirmar CALL como ação ótima universal**.

## 4. Contrato para futura regra V2 (ainda não implementação)

Entrada obrigatória: (a) todas as cartas e avaliação da mão de sete cartas; (b) mão do board e nuts legalmente possíveis; (c) *range do vilão no nó* com combos superiores, inferiores, empates e blefes plausíveis, considerando blockers e ações anteriores; (d) tipo de pote e atores, posição IP/OOP, stack efetivo/SPR; (e) preço no river e ações legais.

Revisão obrigatória:
- Identificar mãos **superiores que o vilão realmente pode ter** e distingui-las de mãos meramente imagináveis que nunca alcançam a linha.
- Separar **ações de valor que perdemos** / **valor inferior que ganhamos** / **blefes que ganhamos** / empates.
- Revisar blockers do Hero sobre as primeiras e últimas categorias; não atribuir blefes universalmente.
- Dimensionamento da aposta: bet de 20%, 50%, 100% ou 200% muda a proporção de mãos inferiores/blefes necessária a um call; não deve impor fold sem passar pelo range.
- Um check gratuito é preferível a fold quando não há aposta a pagar; eventual bet/raise não é excluída por textura four-flush.
- Para multiway, não reutilizar diretamente a frequência de blefes HU.
- Quando o range/histórico não é observável, registrar **INSUFFICIENT_EVIDENCE** para estratégia fina; não fabricar ação `GTO`.

## 5. Gate e próximos passos
- **PASS** apenas para o fato da hierarquia de cartas, exemplos e identificação do erro legado.
- **OPEN** para decisão Call/Raise/Fold no spot: faltam linha, posição, pote, bet, rake e ranges, além da fonte profissional aplicável.
- **NOT TO DO:** não alterar V1, não criar nova política OPPL, não rodar solver, não promover ao runtime.
- Na futura implementação, criar testes independentes de semântica para as oito testemunhas acima; conferir classificador OpenHoldem de `HaveFullHouse` / `HaveNuts`, precedência e ação final, não apenas reproduzir uma especificação genérica.
