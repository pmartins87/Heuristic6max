# F1-FAMILY-DEFENSE — Decisão contextual diante de apostas e raises, em qualquer street

**Data:** 21/11/2026. **Status:** `F1_SPECIFICATION` (especificação de família, **não** política F2 aprovada, **não** código OpenPPL). Orientada por [GENERAL_POLICY.md](../GENERAL_POLICY.md), [DEEPCRUSHER_TRANSFER_AUDIT.md](../DEEPCRUSHER_TRANSFER_AUDIT.md), [PLAN.md](../PLAN.md) e referências profissionais publicadas.

## 1. Problema que esta família resolve

Não codificar `top pair -> fold`, `flush -> call`, `nuts -> raise` ou `board scary -> fold`. Cada decisão considera **qual preço existe, quem chegou à street, quais mãos o vilão pode ter, quais das mãos de Hero vencem qual parte do range e quais linhas futuras existem**. Um full house contra four-flush foi **um alerta**, não o domínio desta família.

A família cobre:
- flop/turn/river, iniciador do pote vs caller, IP/OOP;
- potes SRP, 3bet/4bet/limped/iso, HU e multiway;
- enfrenta aposta inicial, re-raise depois de bet, check-raise, donk/probe, shove;
- stacks baixos/médios/deep **mediante SPR e effective stack**;
- nuts, value muito forte, value vulnerável, bluffcatchers, draws, air e blockers.

## 2. Contrato canônico de decisão (sem fórmulas de solver)

`spot = (street, pot_family, preflop_origin, players_dealt, players_flop, active_players, positions, initiative_by_street, actual_actions_ordered, hero_hole_cards, board_runout, best_five_cards, contribution_hole_cards, legal_nuts, villain_value_range, villain_bluff_range, villain_draw_range, effective_stack, SPR, pot_before_bet, amount_to_call, raise_options, opponent_profile_evidence, rake_rules, observability_status)`

Campos desconhecidos não são automaticamente `false` nem fabricados. Se a fonte OH não os observar, marcar `UNKNOWN` e **não liberar ação operativa**; a especificação estratégica pode continuar em estudo.

**Fronteira de separação importante:** `FacingBet` não equivale a `FacingRaiseAfterOurBet`; `HU_after_multiway_folds` não equivale a mesa originalmente heads-up; `flop_CBet` não equivale a `turn_Probe`. Preservar cronologia.

## 3. Decisões candidatas por estrutura do range e tipo de mão

| Classe de mão / situação | Raciocínio geral de referência | Contraexemplo obrigatório antes de autorar ação |
|---|---|---|
| Nuts/effective nuts | Não desistir por rótulo de textura; avaliar valor de call vs raise, indução, blockers e possibilidade de valor inferior continuar | Alguns nuts checkam para induzir e um raise pode expulsar todo valor inferior; *não* exigir raise universal |
| Muito forte porém não-nuts (full house, flush alto, set etc.) | Diferenciar mãos superiores **plausíveis no range que apostou** de mãos apenas teoricamente possíveis; preço e histórico orientam continuar | River pareado, straight flush e full houses maiores são legais; grande bet contra range de valor muito restrito pode justificar fold excepcional |
| Value vulnerável (top pair, overpair, two pair, straight/flush baixos) | Revisar equity retention e se a linha permite showdown barato, thin value, proteção ou pot-control | No SPR baixo top pair pode stack-off; no deep SPR o mesmo par pode ser insuficiente; não universalizar |
| Bluffcatcher | Estimar se o oponente representa valor que ganha/valor inferior/blefe; blockers das mãos de valor e blefe afetam qualidade do call | Um blocker pode **reduzir blefes do vilão**; não declarar que "blocker de nuts = call" sempre |
| Draws / combo draws / backdoors | Checar outs limpos, nuts possíveis, pot odds, fold equity e showdown value; decidir entre call, semi-bluff raise e fold | Draw dominado, river sem cards por vir, ou multiway/overbet extrema mudam profundamente valor |
| Air com blockers | Blefar só quando representa range crível, possui fold equity e linha coerente; checks e folds continuam necessários | Blefe automático em textura scary perde quando vilão tem range inelástico ou já está all-in |
| Mão desconhecida, scrape inconsistente | Suspender promoção/ação do módulo; informar falha de observabilidade | `Beep`/no-match OpenPPL não demonstra ausência de fallback do autoplayer |

**Não há frequência fixa universal de call/fold/raise por categoria.** Ações que variam por mistura legítima podem ser discretizadas **quando não ampliam erros estratégicos materiais**; registrar incerteza, não dizer “GTO exato”.

## 4. Regra elementar de preço, em todas as streets

Se havia `P` no pote **antes** de o adversário apostar `B`, e Hero precisa pagar exatamente `B`, o break-even de equity num call com realização integral (sem rake, sem apostas futuras e sem empates) é:

`equity_min = B / (P + 2*B)`.

Se o símbolo `PotSize` **já inclui o bet adversário**, a forma correspondente é `AmountToCall / (PotSize + AmountToCall)`. Os símbolos/units reais OpenHoldem precisam ser verificados. Esta é **matemática básica de decisão**, não resolver árvore de solver. Multiway, rake, implied odds e futuras apostas quebram essas simplificações e exigem tratamento distinto. Uma chance de conseguir a mão que ganha **não é automaticamente** equity realizável.

## 5. Metamorfismos e riscos que valem para todos os tipos de pote

- **Consistência de rank:** melhorar categoria da mão não pode ser interpretado como piorar a categoria por mudança de naipe no board; não confundir flush comum e full house.
- **Consistência de cartas:** combinações superiores impossíveis por blockers não podem ser contadas no range; cartas repetidas invalidam estado.
- **Separação preço/contexto:** preço zero disponibiliza check; receber uma aposta muda preço/defesa, mas não a classe objetiva de mão.
- **Ordem dos eventos:** flop bet-call vs flop check-raise não podem compartilhar origem por coincidirem em `AmountToCall`.
- **Transição de jogadores:** ao passar de multiway para HU, não apagar quais jogadores viram streets anteriores; ranges resultantes permanecem diferentes.
- **Profundidade:** mesmo par/draw enfrenta decisões distintas quando SPR e comprometimento mudam.
- **Range e blockers:** uma linha de aposta pode representar full house raro e uma quantidade grande de blefes; comparar ambos, não foldar porque o nuts possível existe.
- **Controle de balanceamento:** apostar 100% dos combos de certo tipo ou nunca blefar river não é presumido; verificar composição da faixa por linha.
- **Ação legal:** se vilão já está all-in não existe raise adicional que tenha sentido naquela ação; proteger min/max e sidepots.
- **Ambiguidade:** ausência de dados ou conflito de símbolo não vira fold automático.

Não exigir monotonicidade de **ação** quando aumenta a força da mão; slowplay, bloqueios e indução podem criar exceções legítimas. Exigir monotonicidade apenas de **rank de showdown** para um mesmo board quando comparamos classificações válidas, observando que trocar cartas pode mudar blockers.

## 6. Fontes e limites de aplicabilidade

- [GTO Wizard — Stack-to-Pot Ratio](https://blog.gtowizard.com/stack-to-pot-ratio/) compara stack-off em SPR baixo/médio/profundo; orienta variáveis, **não** valores universais de raise/call.
- [GTO Wizard — The Right Way To Think About Protection](https://blog.gtowizard.com/the-right-way-to-think-about-protection/) discute equity retention e effective nuts dependentes da profundidade.
- [GTO Wizard — Understanding Blockers in Poker](https://blog.gtowizard.com/understanding-blockers-in-poker/) mostra importância das combinações específicas.
- [GTO Wizard — Why Your Poker Range Is a Team](https://blog.gtowizard.com/why_your_poker_range_is_a_team/) mostra necessidade de formar ranges de valor/blefe/check com coerência de streets futuras.
- [GTO Wizard — How to Analyze Turn Textures](https://blog.gtowizard.com/how-to-analyze-turn-textures-in-poker/) vincula o turn ao histórico do flop/pré-flop.
- [GTO Wizard — Playing in Position Against Two Callers](https://blog.gtowizard.com/playing-in-position-against-two-callers/) evidencia mudanças em c-bet multiway.
- [Upswing Poker — How to Simplify Your Poker Strategy Without Sacrificing Value](https://upswingpoker.com/simplify-your-poker-strategy/) sustenta simplificação de *alguns* nós de decisão; não prova ausência de custo em todos.

**Fonte legacy comparativa:** R10d para classificadores e roteadores; a qualidade de suas ações é **não certificada para cash 6-max**. Nenhuma tabela de soluções proprietárias foi importada.

## 7. O que falta para F2 desta família, sem frear o restante do desenvolvimento

- Escolher **subfamílias de maior risco/recorrência** através dos 14 requisitos de cobertura (por exemplo enfrentar flop bet HU, turn barrel, river bet polarizada, check-raise, aposta multiway) e construir contratos de ações por classes de ranges, não por um único combo.
- Para cada subfamília: um spot contextualizável por fonte profissional, alternativas call/raise/fold/check, razões de valor/blefe, sizings plausíveis e contraexemplos; não transferir thresholds exatos do R10d.
- Continuar auditoria de arquitetura/observabilidade em paralelo ao F3 piloto OpenHoldem; **a pendência de runtime do piloto não bloqueia pesquisa estratégica**, mas bloqueia certificação de código que venha a operar mesas.
- A primeira tranche só conta como **estratégia revisada F2** quando houver decisões concretas por classes e revisão contraditória; este arquivo **não** aumenta a contagem atual de 2 decisões pontuais ou a cobertura 14/14.
