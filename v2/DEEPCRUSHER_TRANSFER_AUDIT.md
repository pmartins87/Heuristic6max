# DeepCrusher R10d → cash 6-max V2 — auditoria transversal de reaproveitamento

**Data de origem:** 21/11/2026; **revisão:** 22/11/2026 (ADR-054). **Estado:** triagem efetiva de funções e integração seletiva de roteadores; **NENHUMA política de aposta SpinGo importada**. Controle por [Política ADR-049](GENERAL_POLICY.md) e [Plano Vivo](PLAN.md).

## Proveniência exata

- Repositório: [pmartins87/DeepCrusher](https://github.com/pmartins87/DeepCrusher).
- Arquivo: [artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt).
- Git blob SHA: `9f9cba79cdb9dc4438895770cf61a450fb55d17c`; arquivo de 1.325.138 bytes, 725 funções `f$`, 545 listas e 6.021 regras `WHEN` conforme benchmark congelado. **A matriz abaixo é amostral por mecanismos, não certificação de todas as funções.**
- O [status do projeto DeepCrusher](https://github.com/pmartins87/DeepCrusher/blob/main/docs/STATUS.md) classifica R10c como baseline operacional e R10d como candidato de hardening com 36/36 verificações estáticas, **não** promoção no runtime.

## Critério de triagem

- **A — REUSE_ARCH**: abstração de contexto/estado reutilizável **após equivalência OH/integração**. Não significa copiar predicados exatos nem ações.
- **B — REQUALIFY_STRATEGY**: princípio profissional plausivelmente transferível, mas dependente de ranges, posição, potes ou SPR; precisa de fontes externas e contraexemplo.
- **C — REWRITE_ECONOMICS**: lógica/threshold sensível a profundidade, tamanho de pote, estrutura ou modalidade; usar apenas como inspiração.
- **D — PLATFORM_ONLY / QUARANTINE**: dependência de rede, PT4, dados externos ou comportamento não comprovado; não importar na base.
- **E — VERIFY_MECHANICS**: candidato a helper de segurança/avaliação, mas exige testar símbolos e unidade OpenHoldem, sem atribuir força estratégica.

## Auditoria por mecanismos concretos (não por um exemplo isolado)

| Função original R10d inspecionada | Evidência no próprio corpo / escopo | Destino V2 | Impacto transversal e validação necessária |
|---|---|---|---|
| `f$flop_Raise_SRP_Initiative` | Encaminha c-bet com preço zero; separa `Position=First/Last`, respostas a donk/float e novos raises | **A — REUSE_ARCH** | Roteador IP/OOP e estado de agressão pode servir a SRP, 3bet, limp/iso com *novos* nós; conferir ordem de ações e mudanças de iniciativa |
| `f$Init_Hero` | Usa `didbetsizeround_previousround`/`didraisround_previousround` e descarta pré-flop | **A, sujeito a E** | Conceito de iniciativa atravessa streets; nem toda aposta anterior do Hero significa c-bet atual; distinguir ator/ação cronológica |
| `f$pot_SingleRaised` | Usa `RaisesBeforeFlop`, `BotRaisedBeforeFlop` e isolamento | **A, sujeito a E** | Classificar origem SRP vs iso; validar captura de raises por jogador, não inferir RFI pela palavra `Raised` |
| `f$pot_Reraised` | Combina `didbetsizeround_preflop`, `didraisround_preflop`, `didcallround_preflop` e `RaisesBeforeFlop` | **A, sujeito a E** | Pot 3bet/4bet, caller vs aggressor e histórico não devem ser confundidos; o predicado original é amplo |
| `f$BoardERROR` | Verifica combinações inconsistentes de `$$cr0..$$cr4` por street | **E — VERIFY_MECHANICS** | Critério de integridade de board em **todas as streets**; sem scraping/estado íntegro não se toma decisão |
| `f$EffectivePotSize_BKP` | Divide `EffectivePotSizeInDollars` por `f$bblind_BKP` quando positivo | **E — VERIFY_MECHANICS** | Unidades e backup de blind/pot são reutilizáveis como *problema de segurança*, não como fórmula validada para qualquer sala |
| `f$pot_Odds` | Mistura `AmountToCall`, `EffectivePotSize_BKP`, status all-in e stacks em ramificações distintas | **C / E — NÃO COPIAR FÓRMULA** | Pot odds imediatas e compromisso futuro são conceitos distintos; revisar denominadores e ações, inclusive para all-in, preço e side pots |
| `f$hand_1HC_Flush` | `HaveFlush && nsuitedcommon = 4`; comentário delimita 1 hole card e four-flush no board | **E — VERIFY_MECHANICS** | Importante para classificar contribuição real das hole cards, flush no board vs mão própria; não é decisão de bet/call/fold |
| `f$hand_2HC_Flush` | `HaveFlush && SuitsInHand = 1 && nsuitedcommon = 3` | **E — VERIFY_MECHANICS** | Não inferir do nome que `SuitsInHand = 1` significa algo sem o manual; testar semântica de contagem antes de reutilizar |
| `f$hand_TopPairOrBetter` | Une `HaveTopNonBoardPairedPair`, pocket overpair e `f$hand_OverPairOrBetter` | **E / B** | Categoria ampla para **descrever**, não para decidir universalmente; força relativa muda por board/range/SPR |
| `f$flop_dry` | Usa `f$flop_dry_HU` se `OpponentsAtTable=1`; senão muda os critérios pelo número/força de draws | **B / E** | Textura é útil em todos os tipos de pote, mas classificador HU native não equivale a cash 6max HU pós-folds; revisar semântica |
| `f$flop_DrawHeavy` | Inclui condição especial `f$game_HUBB` com `WheelPossible`/Broadway; draw heavy = construção dependente de topology | **B / E** | Reavaliar texturas straight/wheel e mão do board; remover suposições 3-handed e não aceitar nomes sem semântica |
| `f$move_flop_cbet` | Ramo de 484 linhas com `f$game_HUSB`, `f$game_3wBTNvBB`, `f$hand_...`, `f$GreenGuy`, `user_...`, `Flop33/40/50` e `EffectiveStack_BKP <=16` | **B / C — TRIAR SUBRAMOS, NÃO PORTAR INTEGRAL** | C-bet é **um** exemplo entre vários; extrair valor/blefe/controle, conferir fonte profissional e adaptabilidade para 100/200 BB |
| `f$BetsizeFlopHeadsup` | Encaminha bet/raise por `user_...`, pot/stacks e valores exatos de raise como 1,5, 2,25 e 6 BB; contém stacks all-in | **C / E** | Reaproveitar separação entre decisão e sizing; **não** transplantar numerais 25BB para deep cash |
| `f$RegHU` e `f$pt_*` | Perfis por `colourcode`, rede/cliente, PT4 e limiares de histórico | **D — QUARANTINE** | Sem observabilidade/consentimento e amostra de dados, não usar classificações fixas como base do bot; perfis devem ter fallback por amostra |
| `f$EffectiveStack_BKP` e `f$stack_*` | Define faixas específicas de stack e backups; a R10d corrige `f$stack_25_UP` para `>25bb` | **C / E** | Necessidade de stack efetivo é universal, **faixas 8–25BB não**; categorias novas para 40/60/100/200BB exigem revisão contextual |

## Outros mecanismos a auditar com a mesma disciplina

A amostra acima **não limita** o universo de reaproveitamento. Prosseguir sobre todas as seguintes famílias, sem ficar apenas no flop/c-bet:

1. **M01/M04:** pré-flop RFI, cold-call, 3bet, 4bet/5bet, squeeze, limp/iso, steal/defesa de blinds — portabilidade de pot origin e seleção de range; ação short stack necessita revisão.
2. **M02/M03:** c-bet, delayed c-bet, probe/donk, floats, check-raise, defesa contra raises, potes 3bet/4bet — aproveitar roteadores e memória.
3. **M05/M06:** potes multiway e a transição multiway→HU, sem reduzir a posição/ação a estado de heads-up nativo; preservar quem saiu e quem ficou.
4. **M07:** memória cronológica `user_...`, agressor por street, bets/calls/raises, reset por mão e estados de observabilidade não confiáveis.
5. **M08:** avaliador de made hand, contribuição de hole cards, paired/dry/wet/monotone, draws, blockers, effective nuts e alterações da textura no turn/river.
6. **M09/M11/M12:** pot odds, sizing, SPR, stack efetivo, all-in e ação legal — controles mecânicos transferíveis, limiares estratégicos não.
7. **M10:** perfil/tendência de adversário com tamanho de amostra e fallback, sem importar identificação de jogador/cliente.
8. **M13/M14:** portabilidade OpenHoldem, fallback, revisão de estratégia profissional, falhas graves e validação em famílias representativas.

## Contraditório com referências profissionais (sem rodar solver)

- [Upswing — How to Simplify Your Poker Strategy Without Sacrificing Value](https://upswingpoker.com/simplify-your-poker-strategy/) compara, num **spot particular T72r**, estratégia complexa e simplificações com pequena diferença de EV publicada. A conclusão transportável é **simplicidade pode ser válida**, não que todos os flops devam ser c-bet 100%.
- [GTO Wizard — Stack-to-Pot Ratio](https://blog.gtowizard.com/stack-to-pot-ratio/) documenta diferença material de stack-off com SPR baixo, médio e profundo; contradiz cópia literal de thresholds Spin&Go.
- [GTO Wizard — The Right Way To Think About Protection](https://blog.gtowizard.com/the-right-way-to-think-about-protection/) destaca valor futuro robusto e que a relevância dos effective nuts depende da profundidade. Não confundir “made hand forte” com auto stack-off.
- [GTO Wizard — Playing in Position Against Two Callers](https://blog.gtowizard.com/playing-in-position-against-two-callers/) descreve redução de frequência e de sizing em muitos spots multiway vs HU, sem regra universal para todos os boards.
- [GTO Wizard — How to Analyze Turn Textures](https://blog.gtowizard.com/how-to-analyze-turn-textures-in-poker/) enfatiza que a textura de turn precisa ser interpretada a partir da história flop/pré-flop e das faixas filtradas.
- [GTO Wizard — Understanding Blockers in Poker](https://blog.gtowizard.com/understanding-blockers-in-poker/) distingue remoção de combos reais de meros rótulos de mão e adapta ações a boards e ranges.

**Todas são referências educacionais; não copiar outputs/charts proprietários como dataset nem assumir licenças.**

## Produto de análise e próximo incremento

**Concluído nesta revisão:** triagem *com leitura dos corpos* de 16 mecanismos concretos, incluindo classificador de mão/board, roteamento, histórico, odds, sizing, stack, perfis e c-bet. Isso **não certifica nenhum deles** em OpenHoldem nem aprova ação estratégica nova.

**Recomendação de próximo incremento estratégico (F1/F2 paralelo ao OH):** contrato por *famílias de decisões*, começando por **defesa vs agressão em todas as streets** (made muito forte, valor vulnerável, bluffcatcher, draws, air), considerando posições, histórico, tamanho da aposta e número de adversários. É transversal e corrige a classe de erro ilustrada por full house four-flush **sem se limitar ao full house**.

**Regra de parada:** não portar `f$move_flop_cbet`/módulos inteiros por quantidade de regras nem transformar cada item acima em projeto de microtestes. Só avançar código quando a primeira família estiver fundamentada, roteada e com contraexemplos estratégicos.


## Revisão obrigatória concluída — ADR-054 (22/11/2026)

**A auditoria anterior NÃO foi esquecida.** Sua classificação `A — REUSE_ARCH` foi aplicada à v0.5 após leitura do `CrusherTBP(2).txt`, `DeepCrusher(1).txt`, blob R10d `9f9cba79cdb9dc4438895770cf61a450fb55d17c` e manual OpenPPL. O resultado detalhado está na [nova matriz específica de histórico](LEGACY_HISTORY_REUSE_20261122.md) e [código v0.5](bot/DeepPoker_V2_Cash6max_v0_5_CRUSHER_HISTORY_REUSE.oppl). A matriz abaixo foi reavaliada: 

- `f$pot_Limped` e `f$pot_SingleRaised`: **A**, com guarda pós-preflop e partição explícita para reraised; sem tratar unopened preflop como limped.
- `f$pot_Reraised`: **A/E**, não copiado: antes do Hero decidir, `RaisesBeforeFlop AND NOT didcallround_preflop` pode descrever um open adversário ainda sem resposta, não uma 3bet consumada. A v0.5 usa dois raisers comprovados (Hero+vilão ou 2 raises oponentes) e não confunde inicial RFI com pote reraised resultante.
- `f$Init_Hero`/`f$Init_Villain`/`f$Init_Nobody`: **A/E**, tradução para `BotIsLastRaiser` + evidência de bet/raise na street anterior, com identidade singular só quando `OpponentsOnFlop=1` e `OpponentsLeft=1`. A antiga checagem “Hero apostou em algum momento” não demonstra ter sido o agressor final.
- `f$Init_GotRaised_Or_Isolated`: **A apenas como conceito**; não copiar registradores `me_st_`/`me_re_` sem reset nativo por mão comprovado. Classificar perda de iniciativa em HU quando houve agressão de ambos e Hero não terminou como último raiser, **sem inventar ordem de check-raise**.
- `user_` histórico da R10d: **A com contrato ADR-053**, flag marca intenção e exige confirmação nativa para afirmar ação real. Na v0.5 foi acrescentado `user_DP_PF_ISOIntent`, ao lado de `user_DP_PF_RFIIntent`, para origem de pote — ambas devem ser mutuamente exclusivas.
- `f$pot_Odds`, `f$stack_*`, `f$move_flop_cbet` e sizings 25BB: permanecem **C/B**, **nenhuma importação de estratégia de torneio**.

**Status:** ADR-053 mantida e refinada; ADR-054 vigente; v0.5 ainda não foi carregada no OpenHoldem e não é liberada para jogar. **Próxima leitura obrigatória:** este documento, [Plano Vivo](PLAN.md), [Ledger](DECISION_LEDGER.md), [Modelo Histórico](HISTORY_MODEL.md) e fonte candidata, antes de alterar roteamento/decisões novamente.
