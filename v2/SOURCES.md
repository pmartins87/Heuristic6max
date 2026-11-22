# V2 — Catálogo F0 de evidência estratégica independente
**Criado:** 21/11/2026 • **Status:** TRIAGEM, NÃO APROVA REGRAS. Documento subordinado a [PLAN.md](PLAN.md). Atualizar este catálogo quando fonte, premissa, direito de uso ou conclusão mudar.

## Protocolo
Registrar fonte + link + cenário efetivamente analisado + hipóteses (NLHE cash/tournament, 6max/HU, stacks, rake, sizings) + qual informação é **evidência textual** e qual é **nossa inferência** + direito de incorporar dados + decisão adotada/controversa. Não converter tabela pública em asset distribuído automaticamente; usar acesso público para pesquisa não cria licença. Não executar solver próprio nem exigir outputs por combo.

## Referências qualificadas para leitura / pendências

| ID | Fonte verificável | Indicação útil | Limites e direitos | Estado |
|---|---|---|---|---|
| SRC-001 | [Upswing Poker — Preflop Poker Charts and Ranges](https://upswingpoker.com/charts/) | RFI online 6-max publicado por posição; exibe, entre outros exemplos, BTN size 2.5BB e taxa agregada de RFI 43.1% na versão consultada | Chart RFI, **não** resposta a 3bet/4bet; rake, premissas completas e direito de transcrição para um bot ainda não demonstrados. Conferir tabela por combo e uso permitido antes de implementação | **CANDIDATE** |
| SRC-002 | [GTO Wizard — The Mechanics of C-Bet Sizing](https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/) | BTN vs BB: exemplos documentados de cbet pequena em QQ6 rainbow; preferência por aposta maior em KJ7 two-tone e estratégia diferente em QJT monotone | Os exemplos pertencem a árvores e ranges específicos; frequência/sizing **não são regras universais**. Artigo educativo, não licença do banco de soluções | **CANDIDATE** |
| SRC-003 | [GTO Wizard — Maximizing Value on Monotone Flops](https://blog.gtowizard.com/maximizing-value-on-monotone-flops/) | Análise publicada de rivers four-flush; existem value bets, checks e bluffs, contrariando `nunca blefar / sempre dar check` | Exemplo é linha/posição específicos. Não transferir percentuais para board pareado com full house sem verificar topologia | **CANDIDATE** |
| SRC-004 | [GTO Wizard — Do Multiple Sizes Matter?](https://blog.gtowizard.com/do-multiple-sizes-matter/) | Evidência didática para simplificar árvore de sizings; erro potencial de simplificação cresce ao aproximar-se do river | Não prova que uma simplificação própria tenha baixa perda EV; exige contrato por cenário | **CANDIDATE** |
| SRC-005 | [DeepCrusher_R10d — artefato canônico do projeto](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt) | Roteamento detalhado, funções de pós-flop, contexto SRP/cbet, memória, sizing, histórico e benchmark de 14 capacidades | R10d é hardening candidate com estratégia legada e premissas Spin&Go; uso como arquitetura/cheque de completude, **não** como gabarito GTO cash 100BB | **ENGINEERING_REFERENCE** |
| SRC-006 | [GTO Wizard — Terms of Service](https://gtowizard.com/terms/) | Registra restrição contra monetização/uso comercial de ranges, trees e charts obtidos no serviço | Sem autorização explícita, proibir incorporação/distribuição de dados proprietários no bot; pode estudar artigos conceituais | **RESTRICTION** |

## Invariantes pré-aprovados como fatos do jogo (não como ações)
1. Full house derrota flush comum; four-flush é textura, não classificador da melhor mão.
2. Em river four-flush + board pareado, o full house do Hero pode perder para full house maior, quads e/ou straight flush dependendo das cartas disponíveis; **não** impor `never fold` universal.
3. Ação de poker depende do range que alcançou o nó, não apenas categoria nominal da mão; preço e bloqueios alteram comparação.
4. Pote sem aposta permite check; aplicar fold por falha de classificação de um check gratuito é erro operacional.

## Primeiro caso candidato e parada
**F0-A:** selecionar chart RFI BTN 6-max ~100BB com premissas declaradas e política legal de uso. A primeira regra somente será escrita após conferir classes, frequências/mixes, posição, sizing e alternativas. Em paralelo, selecionar 3 famílias de textura para SRP BTN vs BB e casos de regressão contra `M08-RIVER4` que não copiem aquele limiar.

**Ainda não resolvido:** correspondência exata de rake/cap e sizes, licenças, direitos de transcrição, cobertura de calls/3bets e versão de solução por combo. **F0 = OPEN; F1–F5 = BLOCKED; regras aprovadas = 0.**

**Critério de parada F0:** se uma fonte não autorizar incorporação de charts, usar os artigos apenas como orientação de princípios, buscar fontes reutilizáveis explicitamente licenciadas e/ou elaborar heurística original com demonstração por lógica e contraditório; não copiar o dataset. Se duas fontes conflitarem materialmente, registrar divergência e não aprovar a ação até reconciliar hipóteses.

## F0-A: divergência objetiva entre referências pré-flop BTN (verificação 21/11/2026)

| Fonte | Jogo explicitado | Abertura BTN RFI | Limitador |
|---|---|---|---|
| [Upswing/Ryan Fee, *My Unexploitable Preflop Opening Strategy Explained*](https://upswingpoker.com/preflop-open-strategy-rfi-explained/) | **6-max cash, 100BB efetivos** na tabela | **40,9%** | Artigo explica contexto 100BB; estratégia introdutória, não certificação GTO. |
| [Upswing, *Preflop Poker Charts and Ranges*](https://upswingpoker.com/charts/) | **online cash 6-max**; o excerto público **não especifica stack/rake** | **43,1%, open 2,5 BB** | Não afirmar que é o mesmo modelo de 100BB. |
| [ART/GTO, *Free GTO preflop ranges*](https://artgto.com/learn/ranges/) | **6-max cash, 100BB**, com **open BTN 2BB** | **46,5%** | Sizing diferente; proíbe uso comercial sem permissão. Não combinar com range de abertura 2,5BB como se fosse mesmo nó. |

**Conclusão F0-A:** o desacordo numérico **não** demonstra erro em nenhuma fonte. Pode refletir árvore/sizing/rake, atualização e nível de simplificação. Para um primeiro nó BTN RFI com 100BB e sizing 2,5BB, o artigo Upswing/Ryan Fee é a referência contextual inicial mais explícita das duas Upswing; ainda **não é autorizado importar o chart** nem declarar política aprovada. Atribuir cada número à sua fonte, não escolher uma média, nem substituir chart sem premissas.

## F0-B: referência publicada para estratégia pós-flop sem resolver solver

- [GTO Wizard, *Flop Heuristics: IP C-Betting in Cash Games*](https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/) — estuda BTN vs BB SRP, ressalvando que a referência exibida é uma solução `Simple` em que BB não pode donkar; paired/high/dry mudam frequência, A-high não implica cbet máxima; connected/monotone diminuem frequência e/ou size. **Admissível como orientação condicional, não regra universal nem output reutilizável**.
- [GTO Wizard, *The Art of Bluff Catching*](https://blog.gtowizard.com/the-art-of-bluff-catching-2/) — documenta composição de value/bluffs, blockers, pot odds e histórico; ensina que mãos fortes podem virar bluffcatchers se não vencerem o range de valor, mas também que calls podem vencer valor pior. **Não é solve do nosso caso full house**.
- [GTO Wizard, *Principles of River Play*](https://blog.gtowizard.com/principles-of-river-play/) — referência suplementar sobre ranges, blockers e sizing no river.
- [Estudo de caso V2 do four-flush pareado](cases/RIVER4_PAIRED_Q9_FULLHOUSE.md) — enumera testemunhas objetivas e demonstra falha de precedência `!HaveFlush && !HaveNuts` sobre full house; **aprova fatos do jogo, não ação específica**.

## F0-C: licenças e admissibilidade de datasets

- [ART/GTO](https://artgto.com/learn/ranges/) oferece 2.606 arquivos públicos para **uso pessoal**, proíbe uso comercial sem permissão. Não importa-los no bot com finalidade comercial nem redistribuí-los sem autorização.
- [jensbaagaard/poker-practice](https://github.com/jensbaagaard/poker-practice) declara MIT e dados `openSourcePokerData` livres. [Proveniência](https://github.com/jensbaagaard/poker-practice/blob/main/data/openSourcePokerData/README.md) indica extração de chunks de um aplicativo externo. **O rótulo MIT do repositório não comprova licença dos ranges extraídos**; marcar QUARANTINED_RIGHTS até esclarecer titularidade original. O próprio repositório contém exemplos pós-flop gerados por TexasSolver; não precisamos executar esse solver.
- [marcbara/jev-preflop-poker](https://github.com/marcbara/jev-preflop-poker) tem código MIT com ranges **manualmente aproximados**, e ressalva que não são solver exato; pode servir de **checagem heurística** depois de confirmar escopo/licença, nunca como GTO comprovado.
- [RubberDucke825/PokerNow-Analysis-and-Trainer](https://github.com/RubberDucke825/PokerNow-Analysis-and-Trainer) distingue explicitamente código MIT de charts transcritos de PokerCoaching/GTO Wizard que **não são MIT**. Usar como exemplo de cuidado jurídico, não como banco V2.

**Stop-rule:** fontes descritivas bastam para princípios gerais, **não** para reproduzir frequências exatas por combo sem licença e premissas. Não iniciar importação automatizada até superar esse ponto.

## Próxima decisão vinculada ao F0
F0 fica **OPEN**, com comprovação da existência de fontes profissionais e de divergências reais entre cenários. Primeiro candidato **BTN RFI ~100BB/2,5BB** em revisão; a sentinela **RIVER4_PAIRED_Q9_FULLHOUSE** foi auditada por hierarquia, não por solver. F1/F2 permanecem bloqueados para decisões estratégicas concretas. Nenhuma `.oppl` V2 criada.
