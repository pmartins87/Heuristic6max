# DeepPoker V2 — revisão de falhas lógicas sistêmicas (21/11/2026)

**Estado: v0.1 REPROVADA PARA JOGO. v0.2 LOGIC_REVIEW é apenas candidata corretiva.** Não declarar bot pronto, mesmo que a sintaxe aparente esteja correta. O usuário pediu raciocínio de pôquer profundo, não mais certificações burocráticas.

## Falha central: força efetiva versus rótulo do board

O manual OpenPPL define StraightOnBoard como "o board contém uma sequência" e FlushOnBoard como "as cinco cartas do board são do mesmo naipe". Não significa que a mão do Hero seja igual ou inferior. HaveQuads também pode reconhecer uma quadra que está inteiramente no board. **Não é seguro deduzir força relativa por negação do rótulo da textura.**

A comparação correta de showdown no river usa a melhor mão de cinco cartas da combinação de sete cartas do Hero, contra a melhor mão de cinco comunitárias, com desempate de ranks e kickers. O manual do OpenHoldem explica pokerval e pokervalcommon; o C++ CSymbolEnginePokerval.cpp da fonte fornecida os calcula separadamente. **pcbits não demonstra vantagem**: o manual admite que, em empates, a escolha interna dos cinco cartões pode dar preferência a hole cards.

A nova função DP_BeatsBoard usa comparação efetiva no river. Há um caso especial para straight flush: o C++ representa os valores num int, com bit 31 de categoria de straight flush, de modo que comparações assinadas entre categorias podem falhar. Quando Hero tem straight flush e board não, a categoria já determina melhoria; quando ambos têm SF a comparação de rank na mesma categoria permite decidir. Comparar Hero > board é necessário, mas **NÃO prova que Hero ganha do range adversário**.

## 11 provas concretas independentes de showdown

Estas foram conferidas com um avaliador de cinco cartas que enumera combinações de cinco entre as sete, sem solver estratégico nem OH executável.

| Board | Hole cards | Força Hero vs board |
|---|---|---|
| 3♣ 4♦ 5♥ 6♠ 7♣ | 8♦ 9♠ | **melhora:** straight até 9 vs até 7 |
| 3♣ 4♦ 5♥ 6♠ 7♣ | 8♦ 2♠ | **melhora:** straight até 8, embora não-nuts |
| 3♣ 4♦ 5♥ 6♠ 7♣ | K♥ Q♠ | empata sequência até 7 |
| 2♥ 4♥ 6♥ 8♥ T♥ | A♥ K♠ | **melhora:** flush ao A vs ao T |
| 2♥ 4♥ 6♥ 8♥ T♥ | K♠ Q♦ | empata flush ao T |
| 7♣ 7♦ 7♥ 7♠ A♣ | 2♦ 3♥ | empata quadra com kicker A |
| 7♣ 7♦ 7♥ 7♠ 2♣ | A♥ K♦ | **melhora:** quadra com kicker A |
| 5♥ 6♥ 7♥ 8♥ 9♥ | A♣ K♦ | empata straight flush até 9 |
| 5♥ 6♥ 7♥ 8♥ 9♥ | T♥ K♦ | **melhora:** straight flush até T |
| Q♠ J♠ T♠ 9♠ Q♥ | Q♦ 9♦ | **melhora:** full house QQQ99 |
| Q♣ Q♦ Q♥ 9♠ 9♦ | A♠ K♣ | empata full house do board |

## Falhas adicionais identificadas diretamente no v0.1

| Área | Erro original | Correção na v0.2 |
|---|---|---|
| Straight / flush / full house no river | Veto usando somente StraightOnBoard/FlushOnBoard/FullHouseOnBoard | DP_BeatsBoard; cartas e desempate, não veto de textura |
| Quads / straight flush compartilhados | RaisePot baseado apenas na categoria, inclusive em quadro compartilhado | Comparação com board, nuts e kicker; ramo especial para quads no turn |
| Preço | PotSize inclui aposta; limite de call de 0,8 vezes PotSize permitia overbets gigantes | **32 condições** passam a usar PotSize menos AmountToCall como proxy do preço pré-call |
| Iniciativa | BotRaisedBeforeFlop permanece true mesmo quando Hero abre e paga 3-bet | BotIsLastRaiser para iniciativa da street anterior; origem RFI separada |
| Blefe e memória | Bet em flop fora do domínio onde Set user era registrado | Mesmo guarda de histórico aplicado ao Set e ao Bet |
| Draw perdido | Um draw no river podia continuar sendo classificado como draw com cartas futuras | DP_AnyDraw e DP_NutDraw retornam falso no river |
| Stack | SPR alto calculado somente pelo stack do Hero | Em HU, considerar também o stack do adversário |
| Big blind | Call possível quando não havia nada a pagar depois de limpers | Exigir AmountToCall positivo no overlimp; BB tem check |
| Estado de jogo | Sem rejeitar quantidade errada de cartas comunitárias | Guardas de ncommoncardsknown = 3/4/5 por street |
| Código inalcançável | RFI sem raise adversário e reraised pot requeridos juntos | Removida conjunção impossível; usar agressor da street correta |

**Exemplo grave de preço:** antes da aposta há 100 BB; vilão aposta 200 BB; PotSize passa a 300 BB. Regra antiga 200 <= 0,8*300 (=240) aprovava call como se a aposta fosse pequena. A revisão usa 200 <= 0,8*(300-200) (=80), que é falso. Isto não é ajuste decimal: corrige interpretação de unidades.

## Limites que ainda impedem chamar a v0.2 de bot pronto

- Comparar Hero com o board **não estima** o range adversário: valor inferior, mãos superiores, blockers, blefes, linha de bets e pot odds ainda exigem decisões por famílias.
- Uma fórmula de preço usando PotSize - AmountToCall é proxy consistente de custo incremental, não reconstrução universal do tamanho da aposta adversária após múltiplos raises ou sidepots.
- As frequências e sizings originais continuam heurísticas amplas que podem ser ruins em potes 3bet/4bet, multiway, turn/river polarizados, SPR extremo.
- BotIsLastRaiser melhora iniciativa, mas não substitui histórico cronológico completo de ação.
- **Nenhuma execução real no OpenHoldem foi observada** nesta revisão. Não declarar funcionalidade operacional nem rentabilidade.

## Decisão de engenharia

1. **Retirar recomendação de uso da v0.1.** Preservar arquivo como histórico do erro.
2. Manter v0.2 com status LOGIC_REVIEW até a revisão substantiva das árvores e dos 226 WHEN existentes, especialmente ações de call/raise/fold por classe de mão e contexto.
3. Reutilizar os símbolos de avaliação da própria engine em vez de inventar inferências por textura. Testes pontuais de regras objetivas fazem sentido; certificação científica não é exigida.
4. Priorizar revisão completa e depois entregar um arquivo substituto para teste do usuário; não repetir o padrão de prometer uma estratégia pronta sem base lógica.
