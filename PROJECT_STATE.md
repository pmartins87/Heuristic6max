> **ESTADO CORRENTE ADR-054:** v0.5 CRUSHER_HISTORY_REUSE é a candidata atual. Roteadores separaram origem RFI/ISO, família limp/SRP/reraised e iniciativa na street anterior sem pressupor identidade de vilão multiway; usa arquitetura CrusherTBP/R10d com semântica fonte verificada, **não** política 25BB. [Ledger obrigatório](v2/DECISION_LEDGER.md), [Plano](v2/PLAN.md), [Modelo](v2/HISTORY_MODEL.md). V0.1 revogada, V0.2–0.4 históricas; sem OH runtime, GTO ou EV demonstrados.

> **ESTADO V2 ATUAL — ADR-053 / 22-11-2026:** [v0.4 HISTORY_REVIEW](v2/bot/DeepPoker_V2_Cash6max_v0_4_HISTORY_REVIEW.oppl) é a fonte candidata de estratégia, **não liberada para jogar**. A v0.3 foi preservada; v0.1 REVOKED. Há 15 predicados de cronologia nativa HU desde flop, tags de origem RFI com ação confirmada e bluffs de river guardados por ação real. **Não há ranges históricos completos, sizes anteriores exatos, reconstrução de identidade multiway ou OH real observado.** [Decisões vivas](v2/DECISION_LEDGER.md), [Plano](v2/PLAN.md), [Histórico](v2/HISTORY_MODEL.md). Atualizar esses documentos **antes de cada decisão futura**.

> **ESTADO ADR-052 / 22-11-2026:** a v0.1 continua **REVOKED_FOR_PLAY**; a v0.2 preservada; a v0.3 está em **CONTEXT_REVIEW (NÃO JOGÁVEL AINDA)**. Corrigidos bugs de baixo SPR fabricado por overbet, calls não-nuts sem preço, draws classificados como nuts, ações ilegais em side-pot vazio e blefes apesar de raise anterior. [Plano Vivo](v2/PLAN.md), [relatório](v2/bot/LOGIC_REVIEW_20261122.md), [fonte candidata](v2/bot/DeepPoker_V2_Cash6max_v0_3_CONTEXT_REVIEW.oppl). V1 intacta, nenhum solver, nenhuma execução OH demonstrada.

> **ESTADO ATUAL — ADR-051 (21/11/2026):** v0.1 CASH6MAX **REPROVADA PARA JOGO**; v0.2 é candidata LOGIC_REVIEW, não liberada. Foram identificados erros sistêmicos de ranking Hero/board, preço, iniciativa, quadras compartilhadas, draws no river, BB free-check e contexto. [Relatório de lógica](v2/bot/LOGIC_REVIEW_20261121.md), [Plano Vivo](v2/PLAN.md). V1 preservada, sem declarar certificação ou desempenho. Histórico anterior abaixo permanece apenas como registro.

> **ESTADO ATUAL V2 — ADR-050 (21/11/2026):** primeira versão **completa nas quatro streets** disponível para o usuário em [v2/bot/DeepPoker_V2_Cash6max_v0_1.oppl](v2/bot/DeepPoker_V2_Cash6max_v0_1.oppl). Autoria heurística V2 independente, pronta para **primeiro teste do usuário**, não observada em OpenHoldem instalado, sem garantia de GTO/EV/lucro. O usuário testa e relata erro; correção direta no mesmo bot, sem gates formais por regra. [Plano Vivo](v2/PLAN.md) + [guia](v2/bot/README.md). Código V1 congelado.

> **ESTADO V2 — ADR-049 (21/11/2026):** [Plano Vivo](v2/PLAN.md) · [Política geral](v2/GENERAL_POLICY.md) · [Transferência DeepCrusher](v2/DEEPCRUSHER_TRANSFER_AUDIT.md) · [Defesa/agressão F1](v2/families/DEFENDING_VS_AGGRESSION_F1.md). Exemplos de RFI, full house e c-bet **não são escopo exclusivo**. F1/F2 seguem em famílias paralelamente ao piloto F3; F3 STATIC_SYMBOLIC_VERIFIED/OH_PENDING e F4/F5 BLOCKED. Zero módulos estratégicos completos ou runtime OH certificados. O texto abaixo é histórico V1/ADR-048.

> **ESTADO V2 — ADR-048 (21/11/2026):** F0 PASS_CONCEPTUAL / DATASET_IMPORT_HOLD; F1 PASS_PILOT_CONTEXT; F2 OPEN (2 decisões revisadas); **F3 STATIC_SYMBOLIC_VERIFIED / OH_PENDING** (20 testes Python, sem parser C++); F4–F5 BLOCKED. [Plano Vivo](v2/PLAN.md), [piloto](v2/pilot_01/README.md) e [gate OH offline](v2/pilot_01/OH_OFFLINE_EVIDENCE_GATE.md). Nenhum módulo completo, runtime ou lucro validado; V1 LEGACY_UNVALIDATED e imutável.

# Estado atual — Heuristic6max
**Data:** 21/11/2026 | **Checkpoint:** M08-RIVER4 DRAFT / CI-LEAN1 (CI anterior OH-SRC1: 616 execuções, 604 deduplicadas) | **Estado:** G2-a HOLD; R10d floor NÃO ATINGIDO; não operacional.

## Evidências concluídas
- G0: arquitetura e contratos.
- G1: reconstrução e observações **sintéticas**; replays reais do OpenHoldem continuam pendentes.
- G2: RFI 5 × 169 = 845 registros; VS_OPEN 15 × 169 = 2.535; VS_3BET 15 × 169 = 2.535. Todos DRAFT, sem avaliação completa de EV.
- v0.5: 119 testes e decomposição de 4-bet por mão; sem modificar a estratégia da v0.4.
- v0.6: 124 testes locais aprovados; card removal físico nas 1.326 combinações com modelo de 3-bet VS_OPEN; **nenhuma ação ou range foi alterado**. As frequências condicionais de 4-bet ficaram 0,409–1,766 p.p. abaixo dos agregados antigos nos 15 nós.
- Dos oito nós originalmente MAJOR_REVIEW, sete ainda têm diferenças superiores a 8 p.p. frente à referência publicada após novo condicionamento; BTN–SB apresenta 6,09 p.p. **Os benchmarks têm rake/árvores diferentes; não validam EV nem autorizam ajustes automáticos.**

## Integridade no GitHub
- v0.5 completo em [gto6_heuristic_v0_5/](gto6_heuristic_v0_5/) — 51 arquivos.
- v0.6 histórica em [gto6_heuristic_v0_6/](gto6_heuristic_v0_6/) — 61 arquivos, com errata de manifesto.
- v0.6.1 corrente em [gto6_heuristic_v0_6_1/](gto6_heuristic_v0_6_1/) — 66 arquivos, incluindo verificação corrigida.
- **Errata v0.6:** 50 arquivos-base de conteúdo permaneceram idênticos; o arquivo SHA256SUMS.txt mudou corretamente após ser regerado, apesar do antigo CSV v0.6 ter marcado 51/51 SAME. A v0.6.1 corrige a trilha de integridade, sem alterar a estratégia.
- Reproduzir: cd gto6_heuristic_v0_6_1 && python -m unittest -q; depois python vs3_blocker_audit_v0_6.py. Verifique SHA256SUMS.txt **antes** de regerar qualquer CSV.

## Premissas e limitações
Cash 6-max, 100 BB alvo (95–105), blinds 0,5/1 BB, sem ante, RFI 2,5 BB LJ–BTN e 3 BB SB; sizings fixos de 3bet, sem limpers/callers/squeeze/short stacks, rake não calibrado. Não há estratégia pós-flop, VS_4BET/5BET ou integração operacional OpenHoldem. Nenhum resultado de simulação demonstra lucratividade real, proximidade quantitativa à GTO ou segurança em mesas.

## Próximo gate
G2-a permanece aberto: auditar a composição exata dos oito confrontos com premissas de rake/sizing e frequências de vilão coerentes antes de mudar ranges. Não iniciar VS_4BET até a decisão documentada. G1 exige replays reais em ambiente de teste sem apostas.

## Auditoria v0.7 — nova evidência, sem mudança estratégica
- Código e CSV em [audits/g2a_v0_7](audits/g2a_v0_7/). Total **131 testes locais**: 124 na baseline v0.6.1 e 7 novos de auditoria.
- Medição em 15 confrontos de P(Hero fold | RFI, cartas exatas do agressor) com card removal, testada contra agregação v0.6.
- Sete dos oito MAJOR_REVIEW têm pressão positiva sob **experimento isolado com zero equidade do agressor depois do call/4bet e demais jogadores desistindo**. HJ vs CO: fold 77,54%, break-even 66,67%, EV contrafactual +1,305 BB. SB vs BB: fold 60,76%, break-even 68,25%, EV contrafactual −0,944 BB. BTN vs SB: +0,048 BB é marginal.
- Sem estimar EV verdadeiro: há ações de outros jogadores, rake não calibrado e decisões futuras. Nenhum range RFI/VS_OPEN/VS_3BET foi alterado. G2-a HOLD; G2-b bloqueado.

## Auditoria v0.8 — checkpoint incremental (20/11/2026)
- Código e relatórios: [audits/g2a_v0_8/](audits/g2a_v0_8/), nove arquivos incluindo manifesto SHA-256; **11 testes novos**, total local 142 (124+7+11).
- Massa condicional por mão/família sob RFI+3bet com exclusão de cartas; os totais coincidem com a v0.6.1 nos 15 nós.
- HJ vs CO: 23,2205 pp de folds da família suited-other, 11,2818 pp de pares 22–66, 9,2929 pp de broadways offsuit sem A, 14,3167 pp de Ax offsuit; somados 58,1119 pp dos 77,5377% de fold.
- Análise das ações dos jogadores posteriores: sob o modelo zero-equidade da v0.7 e hipótese adicional de independência, o spot BTN vs SB exige P(nenhum cold action)≥99,51% para EV hipotético não negativo. Não existe medição empírica dessa probabilidade.
- Nenhum range, ação, sizing ou módulo estratégico modificado. Ações de possíveis cold callers, EV verdadeiro, rake/cap e equidade/realização continuam sem validação. Gate G2-a HOLD.

**Errata de reprodutibilidade v0.8:** primeiro CI acusou somente ordem de linhas em classes empatadas (Python 3.11 vs 3.13); script agora usa desempate determinístico. Nenhum cálculo estratégico mudou. Testes incrementais v0.8: 11.

## Auditoria incremental v0.9 — HJ vs CO (20/11/2026)
- [Código, 169 classes, 15 candidatos, 36 cenários de preço, 11 testes e hashes](audits/g2a_v0_9/README.md). Total esperado **153 testes** (124+7+11+11); não é validação estratégica GTO.
- P(Hero fold | RFI HJ, 3bet CO) = **77,53771778%**, CALL = **14,03919921%**, 4BET = **8,42308301%**. Os testes reproduzem a v0.6.1.
- HJ abre AQo, AJo, KQo, KJo, A9o e desiste 100% versus o CO 3bettor na política atual. Não há prova de que esse fold ou o próprio open seja errado.
- Abertura HJ 2,5 / 3bet CO 8 BB: call adicional 5,5 BB, pote após call 17,5 BB, exigência imediata 31,4286% antes de rake/realização. 4bet para 21,2 BB exigiria 60,9121% de folds de todos sob o experimento artificial de blefe com equidade zero.
- Contrafactuais mudar RFI ou defesa são **simulações de frequência, não EV**. Rake/cap e EQR não são dados reais; todos os três CSV de ranges mantidos, status estratégico HOLD.

## Auditoria v0.10 — HJ/CO equities, sem mudança estratégica
- [Método e referência v0.10](audits/g2a_v0_10/README.md), [169 equities por classe](audits/g2a_v0_10/HJ_CO_EQUITY_169_REFERENCE_v0_10.csv), [15 conferências Monte Carlo](audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv).
- A fonte privada fornecida tinha 1.624.350 confrontos físicos ordenados, cobertura/reciprocidade conferidas; licença/autoria não documentadas, portanto **não publicar o bruto**. SHA-256 da fonte e método presentes no README da auditoria. Motor MC em Python stdlib pode reestimar sem a fonte original.
- Ex.: AQo 41,3101%, AJo 35,6951%, KJo 32,3099%, TT 44,0217% de **equidade bruta de showdown** contra a política 3bet do CO. Isso NÃO determina EV de call fora de posição, nem prova que folds existentes estão errados.
- 10 testes novos; total acumulado previsto **163 (124+7+11+11+10)**. Todos os ranges e o snapshot v0.6.1 permanecem intactos; G1 aberto, G2-a HOLD, G2-b bloqueado.

## Auditoria v0.11 — admissibilidade de fontes e fronteira da linguagem
- [Relatório e fontes](audits/g2a_v0_11/README.md), 11 testes incrementais, total acumulado **174 testes locais** (124+7+11+11+10+11).
- ART/GTO HJ RFI publicado para abertura 2 BB, não equivale ao nó HJ RFI 2,5 BB enfrentando CO 3-bet para 8 BB. Simple GTO anuncia 2,5 BB e 3,4x IP (8,5 BB inferido, não verificado naquele nó); GTO Wizard não teve rake/sizing/nó exatos confirmados. **Três fontes: zero substituições diretas autorizadas pelo gate**.
- Direitos de incorporação/reprodução, rake e cap do ambiente-alvo seguem não comprovados. Ausência NÃO equivale a rake zero.
- **Python atual; OpenPPL não implementado**. G6 PENDENTE; não existe estratégia OpenPPL jogável.
- **Stop rule:** não repetir simulações de EV baseadas apenas em EQR/rake arbitrários. Próxima evidência necessária: rake/cap/sizings reais, chart compatível e utilizável ou replays reais de teste (G1). Ranges DRAFT intactos, G2-a HOLD, G2-b bloqueado.


## PORT-0: novo requisito explícito de paridade (20/11/2026)
A partir do ADR-016, regras novas de decisão executável devem nascer em OpenPPL ou representação restrita única; Python não terá uma segunda implementação independente da estratégia. [Contrato](PORTABILITY_CONTRACT.md).
Prova estática BTN RFI AA/KK: duas linhas OpenPPL, sete testes e 3.042 estados. Total esperado 181 testes com as suítes anteriores (174+7). NÃO demonstra funcionamento no OpenHoldem real, nem garante fallback seguro.
Python de importação de charts, análise, Monte Carlo, testes e reconstrução offline segue sem limitação artificial. Nenhuma ação/range histórico foi alterado. G1 aberto, G2-a HOLD, G6 pendente.

## PORT-1 parcial — RFI LJ (20/11/2026)

- [Código OpenPPL, testes e fonte única](portability/port1/README.md), [cobertura das 169 classes](portability/port1/PORT1_LJ_169_MAPPING.csv).
- 43 RAISE puros e 125 FOLD puros representados em duas listas/regras OpenPPL; **KJo (40% raise/60% fold) permanece NÃO MAPEADO** para não quebrar a estratégia mista.
- 15 testes incrementais em Python interpretam as regras OpenPPL diretamente, sem estratégia paralela. Contagem total esperada 174+7+15 = **196 testes**.
- **PORT-1 permanece ABERTO**, pois símbolos, sorteio estável, ação ilegal e fallback ainda precisam de teste no OpenHoldem real. Nenhum range estratégico mudou.

**Estado:** G1 e G2-a ainda abertos; G6 pendente. A prova é somente estática e não operacional.

## PORT-2 — 20/11/2026: mistura KJo compatível em fonte, sem promoção
- `portability/port2/`: 169/169 classes LJ RFI representadas em OpenPPL (43 RAISE puro, 125 FOLD puro, KJo misto 40/60 por `randomhand`), derivadas da v0.6.1 imutável.
- 19 novos testes locais de interpretador estático, distribuição em 10.000 limiares, estabilidade com input constante, fronteira 0,40 e rejeição de regras inseguras. Total esperado no CI: 215.
- A **implementação real de randomhand** e ação final OpenHoldem NÃO foram verificadas. `None` em Python não prova fail-closed OH. PORT-2 não aprova G6; G1 aberto, G2-a HOLD e G2-b bloqueado.

## PORT-3 / RPL-0 — auditoria de evidência para replay (20/11/2026)
- [portability/port3/](portability/port3/) contém 7 arquivos novos: auditor offline, **27 testes**, seis registros sintéticos, relatório determinístico, README, .gitignore de evidências privadas e manifesto SHA256.
- Testes locais: 27/27; total esperado na CI: **242**. Relatório exclusivamente sintético: **5 STATIC_ONLY + 1 BLOCKED_NO_MATCH**. **Zero capturas de OpenHoldem real, zero aprovações operacionais**.
- Novos invariantes: hash da fórmula OPPL, mesmo `randomhand` por (sessão,mão), guardas observados, comparação independente de ação da fórmula e ação realmente tomada, RaiseTo exato, evidência auditável e no-match SEM aprovação automática. Um log com hash correto ainda precisa de revisão de autenticidade.
- Não foram alterados ranges RFI/VS_OPEN/VS_3BET, G1 segue aberto, G2-a HOLD, G6 pendente. Próximo passo é capturar replays **offline** do OpenHoldem-alvo; não presumir existência de executável ou logs.

## RFI-MVP — avanço útil de implementação, 20/11/2026
- `portability/rfi_mvp/` tem 7 arquivos: OpenPPL real como fonte de decisão, gerador offline, interpretador estrito, 12 testes, 845 registros, README e SHA256.
- Cobertura first-in 5×169=845: 5 classes de mix (LJ KJo 40%, HJ QJo 50%, BTN 53s 50%, SB K3s raise 50%, SB 97o limp 75%), o restante puro. SB possui estratégia de limp conservada.
- **12/12 testes locais** e 254 acumulados esperados no CI. Testes percorrem 845 classes e vários valores de randomhand; não simulam EV, não garantem compilação no executável OH.
- RFI v0.6.1 *imutável*. Próximo produto de estratégia: VS_OPEN OpenPPL da baseline histórica, sem bloqueá-lo por pesquisa não necessária. G1 aberto, G2-a HOLD, G2-b bloqueado, G6 pendente.

## VS_OPEN-MVP OpenPPL — checkpoint 20/11/2026
- Publicado [portability/vs_open_mvp/](portability/vs_open_mvp/): 8 arquivos (121 regras OpenPPL, 81 listas, 2.535 classes de 15 confrontos, gerador, intérprete da mesma fonte, 19 testes, CSV e manifesto SHA256).
- Incluído **arquivo combinado OpenPPL** com RFI anterior (**21 regras**) + VS_OPEN (**121 regras**) sob **um único `##f$preflop##`**; são **3.380 entradas classificadas** (845 RFI e 2.535 VS_OPEN) — NÃO todos os cenários do jogo. Ações e sizings v0.6.1 preservados.
- Mixes: 3bet/call, 3bet/fold e call/fold nativos via `randomhand`, sem duplicar política Python. FirstRaiserPosition e LastRaiserPosition, posição do Hero, RaiseTo em BB e guardas de stack/ação combinadas; sem replay OH-alvo.
- 19 testes novos: total esperado **273 = 254 +19**. **Ainda não operacional**: no-match/fallback, VS_3BET, jogadores intermediários, pós-flop e paridade OpenHoldem real ausentes. G1 ABERTO; G2-a HOLD para mudanças estratégicas; G2-b bloqueado; G6 pendente.

## Implementação VS_3BET-MVP (20/11/2026)
- [portability/vs_3bet_mvp/README.md](portability/vs_3bet_mvp/README.md). 15 confrontos, **2.535 classes auditadas**, 888 classes alcançáveis pelo nosso RFI e 1.647 inalcançáveis (sem fallback inventado), 90 handlists e 135 regras OPPL.
- Módulo VS_3BET isolado + fonte única **RFI/VS_OPEN/VS_3BET com 277 regras**; 23 novos testes; **277 acumulados esperados em CI** (254+23). Nenhum dos 3 ranges v0.6.1 alterado.
- Contagem correta OH `Raises=1` após RFI do Hero; `BotRaisedBeforeFlop`, `RaisesSinceLastPlay`, `FirstRaiserPosition`, `LastRaiserPosition` e stack inicial da rodada são guardas **a verificar no executável**. Nenhuma medição real OH efetuada.
- **Pronto apenas como código DRAFT**. G1 aberto, G2-a HOLD por qualidade estratégica, G2-b bloqueado, G6 pendente. Não alegar bot operacional ou winrate.

## G3: SRP HU pós-flop em OpenPPL — checkpoint 20/11/2026
- [portability/srp_hu_mvp/](portability/srp_hu_mvp/) implementa **14 regras flop + 10 turn + 9 river**, mais 5 funções auxiliares, com interpretações Python derivadas EXATAMENTE da fonte OPPL (sem outra estratégia).
- Condições de cobertura: 6 jogadores dealt, 1 adversário desde flop, sem oponente all-in, estado conhecido, histórico pré-flop compatível com single-open do bot ou single-call do bot. Há **risco residual de limp/isolation** não distinguido com os símbolos presentes; não afirmar detecção SRP exata.
- Ações: valor com pares fortes/duas-pares+, decisões de draw/price, cbet seca 25% de frequência, turn semi-bluff NFD 30%, river sem blefe; propostas heurísticas NÃO calibradas em EV, nem GTO por solver.
- **18 testes novos** de ação/fallback/símbolo/sintaxe/prioridade e identidade binária do pré-flop. Um único arquivo combinado `preflop_and_srp_hu_draft.oppl`; estratégia v0.6.1 sem alterações.
- **G3 em desenvolvimento**, G1 ainda sem replays OH reais, G2-a HOLD, G2-b bloqueado, G4/G5/G6 ainda pendentes; arquivo NÃO operacional.

## G3-HIST-v1 — caminhos flop→turn→river (20/11/2026)
- [Objetivo completo e critérios](STRATEGY_ARCHITECTURE.md); [código, gerador e 18 testes](portability/srp_history_v1/README.md). O projeto é um bot complexo com árvore de decisões de longa duração e milhares de caminhos planejados; não é experimento científico nem solução exata de GTO.
- Novo pós-flop OpenPPL: **58 regras de ação** (14/16/28), 24 funções booleanas, **9 trajetórias** flop→turn representadas por sinais de ações; arquivo integrado mantém pré-flop (277 regras) literalmente. Tipos B=bet do bot seguido de call, C=check-through, X=call do bot a uma bet.
- **18 testes locais novos**; total esperado na CI **295 = 277+18**. Contradições/raises não classificados retornam no-match no simulador, não Fold. **No-match em OpenHoldem pode acionar fallback**, portanto não há aprovação operacional. Baseline e G3 anterior preservados.
- Gate G3 continua EM DESENVOLVIMENTO: falta ação intra-street, textura/runout, SPR, perfis, 3bet pots, multiway e revisão de histórico em OH-alvo. G1 aberto, G2-a HOLD, G2-b bloqueado, G6 pendente.

## G3-HIST-v2 — segundo incremento nesta rodada (20/11/2026)
- [portability/srp_history_v2/](portability/srp_history_v2/) acrescenta categorias de check-raise pago (H), raise sobre aposta e call adversário (R) e bet nosso→raise vilão→call nosso (M) às três classes anteriores (B,C,X), **36 combinações flop→turn** verificadas por helpers OpenPPL.
- **75 ações (14/22/39)**, 70 funções, 18 novos testes; **total esperado CI 313** = 277 anteriores +18 HIST-v1 +18 HIST-v2. As **9 trajetórias HIST-v1 permanecem equivalentes** em inputs iguais; nenhuma alteração nos 277 ramos pré-flop.
- Más classificações/flags contraditórios ficam sem correspondência no interpretador. OH ainda pode aplicar default.bot, portanto não executar em jogos reais; rastreamento por flags agregado não é um log de eventos verdadeiro. G3 em desenvolvimento e G6 pendente; G1 aberto e G2-a HOLD preservados.
- Próximo ganho real: histórico ordenado de ações com apostas/raises e mudança de posição, classificação do pote SRP versus limp/iso, board texture/runout, SPR e sizings. Não inflar quantidades de nós sem validação de estado.

## G3 HIST-v3 — checkpoint cronológico (20/11/2026)
- **484 históricos legais** de flop+turn chegando ao river (11 cadeias completas de ação por street, IP/OOP e Hero PFR/caller), com cap puramente enumerativo de quatro raises por street. Não há sizing/SPR, all-in, multiway nem 484 ações autoradas. Esses cenários são um **inventário de lacunas**, não uma estratégia final.
- Biblioteca oficial OpenPPL: `OpponentCalledOnFlop/Turn` somente quando `NoVillainBetOrRaised...`; R/H do HIST-v2 podem ser inalcançáveis. HIST-v3 substitui chamadas por classificadores de raise e check-raise baseados em observações da street anterior; preserva HIST-v2 como histórico.
- Três colisões por resumos de flags IP; quatro `Set user...` observacionais capturam Bet versus Raise anterior. A nova rota recusa M IP sem marcador consistente. Sem ação inventada em caso desconhecido; **no-match não é fail-closed no OH real**.
- 10 helpers novos e 31 testes; **344 testes esperados CI**, todas as 75 ações prévias e todo pré-flop preservados. G3 em desenvolvimento; G1 ABERTO, G2-a HOLD, G6 pendente; zero replay real neste checkpoint.

**HIST-v3 cobertura complementar:** interpretador da MESMA fonte OPPL + flags derivados da biblioteca identifica **100/484 cenários permitidos pelo domínio no modelo**, **264 bloqueados pela classificação flop e 120 pela turn**. É um limite superior hipotético de memória perfeita, NÃO taxa de ação operacional; restam 384 lacunas. Agora **36 testes novos, 349 totais previstos**. Regras de ação, ranges e G1/G2/G6 inalterados.

## Novo requisito mínimo — R10d e implementação 3bet HU (20/11/2026)
- Requisito obrigatório: lançamento final deve ter abrangência estratégica e técnica **superior ao DeepCrusher_R10d**, sem tornar-se solver ou pesquisa científica e sem transplantar decisões sem revisão.
- Fonte R10d de 1.325.138 bytes lida diretamente do blob Git `9f9cba79...` (link e checksum em [benchmarks/r10d_floor/](benchmarks/r10d_floor/)); contém 725 f$, 545 listas, 6.021 WHEN, 1.561 Set e 561 símbolos de memória. H6 ativo (p3bet v1) contém 88 f$, 187 listas, 649 WHEN, 57 Set e 6 símbolos user_. **As métricas não medem EV nem equivalência estratégica**, mas a diferença de escala/abrangência é real.
- 14 capacidades exigidas; 14 ainda PARTIAL ou MISSING, 0 totalmente VERIFIED no gate atual. [Matriz](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv). **Não afirmar superioridade, completude, prontidão nem vantagem em poker real.**
- Novo [p3bet_hu_v1](portability/p3bet_hu_v1/README.md): 39 regras de ação flop/turn/river em potes 3bet HU, intent-tags extraídas de 9 raises first-in +44 3bets vs open; domínio exige histórico nativo de bot e 1 adversário. **Sem alteração nas decisões pré-flop v0.6.1**. 15 testes novos no módulo, 12 no benchmark; 376 esperado no CI.
- Faltam sobretudo 4bet/5bet, limped/iso, multiway 3 e 4+, short/deep stacks, memória real cronológica, adversário e runtime OH. G1 ABERTO, G2-a HOLD, G6 PENDENTE.

## SRP 3-way v1 — expansão substantiva da cobertura R10d (20/11/2026)
- [portability/p3way_srp_v1/](portability/p3way_srp_v1/) possui 8 arquivos: 31 ações novas por street 13/10/8, 33 intents de CALL VS_OPEN, 4 helpers, fonte integrada e 16 testes locais.
- Histórico distinto: Hero PFR que enfrentou 2 callers (marcador RFI confirmado por raise efetivo) e Hero caller de um open que chegou a 3 jogadores no flop (marcador CALL confirmado por BotCalledBeforeFlop). **Pote 3-way exige OpponentsOnFlop=2 e OpponentsLeft=2**, sem allin, estado desconhecido ou raises incompatíveis.
- Inventário do H6 ativo passou para 729 WHEN, 92 f$, 187 listas, 90 SET e 7 símbolos user_ versus 6.021 WHEN, 725 f$, 545 listas, 1.561 SET e 561 símbolos user_ no R10d. Isso NÃO autoriza comparação de qualidade.
- A família M05 no piso R10d passou de MISSING para PARTIAL; ainda **14/14 critérios sem aceitação final**, inclusive M05. G1 aberto, G2-a HOLD; G6 ainda não testado em OH. Total esperado CI 392.

## ADR-031 (20/11/2026): conserto de nuts versus overbets
Protegidos flop/turn contra `HaveNuts → Fold` quando o tamanho da aposta excede o preço de call previsto para mãos inferiores. Novos módulos: **41+33 ações**, último integrado 733 WHEN /92 funções /187 listas /90 Set /7 user_. Todos os 14 gates R10d continuam sem validação integral. 392 testes previstos; G1 aberto, G2-a HOLD, G6 pendente.

## Checkpoint ativo — Multiway-v2 + LIMP-BB-v1 (20/11/2026)
- **Nova fonte integrada:** `portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl`. 899 WHEN, 106 f$, 187 listas, 92 Set user, 9 user_ distintos. **434 testes totais esperados** (392 anteriores +25 multiway +17 limped BB).
- [Multiway-v2](portability/multiway_v2/) registra 40 decisões para 4/5/6way SRP sem saídas e 34 quando um pote 3–6way fica HU. [LIMP-BB-v1](portability/limped_bb_v1/) trata check do BB versus single-limp e 33 decisões nas streets seguintes.
- **M04/M06 PARTIAL**, 14 famílias R10d ainda sem VERIFICATION; zero validação OH real, G1 aberto, G2-a HOLD e G6 pendente. Origem pré-flop e topologia ainda precisam de replay. Ranges da v0.6.1 intactos.

## Estado após expansão MWT3/MLIMP2/P3BMW1 (20/11/2026)
- Arquivo ativo: `portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl`, 1.460 WHEN, 136 f$, 187 handlists, 99 SET e 16 user_. Antecessor: 899/106/187/92/9. R10d congelado: 6.021/725/545/1.561/561.
- Ganho de **123 regras de ação pós-flop** (+41 transições SRP, +39 multi-limp BB, +43 potes 3bet multiway) e sete opções BB-check. Modelos de histórico `OpponentsOnTurn` e `OpponentsOnRiver` documentados, sem observação OH real.
- Testes incrementais: 14+12+12 = 38, total esperado **521**. Políticas v0.6.1 e antigas seções WHEN preservadas, inclusive sized raises.
- Piso R10d NÃO ATINGIDO: 14 famílias ainda não VERIFIED; faltam limp/iso, 4bet/5bet, perfil do adversário, SPR/board/runout, stacks, fallback e validação operacional. G1 ABERTO, G2-a HOLD, G6 PENDENTE.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## ISO-1 — isolamento tardio contra limpers (DRAFT, 20/11/2026)
- Em `portability/iso_raise_v1/`, cinco novos nós CO/BTN com 1–3 limpers, handlist separada e 5 intenções `Set`; **nenhum range RFI/VS_OPEN/VS_3BET da v0.6.1 foi editado**. Os 5 limps pré-flop são uma política heurística nova, NÃO validada em EV.
- Pós-flop: 41 ações (15/14/12), 120 topologias monotônicas (15 flop, 35 turn, 70 river), origens mutuamente exclusivas e limites por número máximo de callers; nuts protegido contra overbet. Combinação atual DRAFT: `portability/iso_raise_v1/iso_integrated_draft.oppl`.
- **CI aprovada no commit `142c00eb` ([execução 44853164836](https://github.com/pmartins87/Heuristic6max/actions/runs/44853164836)): 534 execuções em 27 suítes, 522 testes deduplicados por suíte.** São 13 testes incrementais sobre a baseline 521/509. Replays reais OH: **zero**. G1 ABERTO, G2-a HOLD, VS_4BET BLOQUEADO, G6 PENDENTE; 14 capacidades R10d continuam sem aceitação integral. Sem autorização de uso real.

## BLISO-2 — isolamento SB/BB, DRAFT sem OH real (20/11/2026)
- Fonte: [portability/blind_iso_v2/](portability/blind_iso_v2/), derivada do integrado ISO-1 `iso_integrated_draft.oppl`. **13 origens**: SB 1–4 limpers; BB 1–5, distinguindo SB completado de SB não completado. 13 `Set user_H6_BISO*` + `RaiseTo` somente para uma handlist específica; SB residual `Fold`, BB residual **mantém Check antecedente**.
- **43 regras pós-flop** (16/14/13) em 120 topologias legais compartilhadas semanticamente com ISO-1, mas com origem blind-isolation exclusiva. A origem exige marcação de intenção, `BotRaisedBeforeFlop`, exclusão de `BotCheckedPreflop`, `BotCalledBeforeFlop` e 3bet. Decisão de valor HU considera posição SB/BB; `HaveNuts` nunca fold por overbet.
- Novo integrado: `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`: **1.920 WHEN / 152 funções / 189 listas / 117 Set user / 34 símbolos user_**. Todos os 1.666 WHEN anteriores preservados. Ranges RFI/VS_OPEN/VS_3BET v0.6.1 intactos; novos critérios de blind iso não foram avaliados em EV.
- **18 testes incrementais aprovados** no [workflow 44858080418](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418): **552 execuções em 28 suítes, 540 testes deduplicados por suíte**. ISO-1 534/522 é checkpoint histórico. R10d 0/14 VERIFIED, G1 ABERTO, G2-a HOLD, G6 PENDENTE, VS_4BET BLOQUEADO e nenhum runtime OH validado.

## ISODEF-1 — resposta delimitada a isolation raise (21/11/2026; DRAFT)
- Pai: [BLISO-2](portability/blind_iso_v2/README.md); novo integrado: `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`. **2.007 WHEN / 159 f$ / 192 listas / 121 Set user / 38 user_**; todos os 1.920 WHEN anteriores estão presentes na mesma ordem e os ranges RFI/VS_OPEN/VS_3BET v0.6.1 não foram editados.
- Dois nós de resposta ao isolamento: Hero BTN vs CO após 1 limp (pote pré-ação de 7BB, call 4.5BB) e Hero BB vs BTN após 1 limp (call 3.5BB). Três handlists novas, 4 tags de intenção; 42 decisões pós-flop HU/3way sobre 12 topologias históricas, com nós distintos para Hero 3bettor/caller e `HaveNuts` protegido contra overbet. Rejeição explícita de BTN+BB simultâneos após teste negativo.
- **21 testes novos aprovados na CI [workflow 44860943038](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038): 573 execuções / 561 deduplicadas por suíte em 29 suítes**, auditados por registros `Ran N tests`. G1/G6 seguem sem replay real; G2-a HOLD, R10d 0/14 verificados. Não é release/operacional.

## OH-G1G6-1 — instrumentação de prova do executável (21/11/2026)
- Não houve mudança de política poker: último integrado permanece `portability/iso_defense_v1/iso_defense_integrated_draft.oppl` (**2.007 WHEN / 159 f$ / 192 listas / 121 Set / 38 user_**), ranges v0.6.1 e ancestrais preservados.
- Criado [protocolo de evidências offline](portability/oh_runtime_gate_v1/README.md) com dez cenários ancorados em símbolos/regras reais do integrado, coletor PowerShell de hashes **sem abrir nem automatizar OH**, checklist humano, estrutura privada ignorada pelo Git e script que verifica snapshots/arquivos SHA, debug, estabilidade de `randomhand`, par de ações `Best action`/`Action taken`. Não existe resultado `PASS` ou promoção automática: `runtime_approved=false` é incondicional.
- [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886) verde no commit de PR `c0a1eed16fe17212e1cca1d4c117c268d280e55a`: **26 novos testes**, **599 execuções / 587 deduplicadas em 30 suítes**, +26 sobre ISODEF-1 (573/561). Nenhum executável OH, tablemap e replay real disponíveis nesta sessão; evidências de runtime **zero**. **G1 ABERTO, G6 PENDENTE, G2-a HOLD e 0/14 R10d VERIFIED**.

## OH-SRC1 — compatibilidade pela fonte sem dependência da instalação (21/11/2026)
- [Auditoria de semântica](portability/oh_source_audit_v1/README.md) apoiada no C++ `repositorio_completo_openholdem.txt`, na biblioteca `OpenPPL_Library_Integrated.txt` e no manual OpenPPL fornecidos. **17 testes adicionais aprovados na [CI OH-SRC1](https://github.com/pmartins87/Heuristic6max/actions/runs/44864070437) — 616 execuções, 604 deduplicadas por suíte, 31 suítes.**
- Inventário exato: **2.007 WHEN** sem mudança de política; **436 `PotSize = literal`**, 258 `AmountToCall = 0`, 400 igualdades de `AmountToCall` não zero, 103 `StillToAct`, 343 `FirstRaiserPosition`. O risco é de precisão/semântica; nenhum dos 436 foi alterado automaticamente. Duas origens ISODEF-1 mantêm `Set`/ação com guardas idênticas.
- C++ demonstra que `UpdateOnHandreset` limpa flags `user_*`; manual confirma que `Set` continua até a próxima ação. `Calls` depende do estado e histórico; `StillToAct` é válido na primeira órbita. Construção SOURCE-FIRST segue sem qualquer hash do OH local; para certificar executável instalado, fallback e ação efetivamente tomada persistem G1/G6 pendentes. **G2-a HOLD, R10d 0/14 VERIFIED, sem liberação real.**

## CI-LEAN1 — status do ciclo de engenharia
- Auditoria do workflow: **6 regenerações R10d → 1 final**, **2 execuções R10d de 12 testes → 1**, **126 etapas → 113**, **30 comandos de testes → 29**. As outras suítes, geradores e checksums permanecem.
- CI completa apenas em PR pronta e em `main` (ou `workflow_dispatch`); PR draft pula job integral; cancelamento de execuções obsoletas só para a mesma PR. Contagem esperada: **604 execuções de testes em 30 suítes**, sujeita a confirmação em log.
- Fonte estratégica ISODEF-1 permanece intacta; G1/G6 de certificação não aprovados, G2-a HOLD, R10d 0/14. Próxima etapa do projeto: capacidade estratégica material e testes associados, não nova camada de meta-auditoria.

## M08-RIVER4 — novo integrado source-first, ação concreta no river
- [OpenPPL river four-flush](portability/river_fourflush_v1/README.md) passa a ser o integrado ativo: 2.016 WHEN / 161 f$ / 192 listas / 121 Set user / 38 user_; todas as 2.007 regras ancestrais na mesma ordem. Nenhuma alteração nos ranges pré-flop ou em potes ISO, 3bet e multiway.
- River com exatamente quatro do mesmo naipe (`OneCardFlushPossible AND NOT FlushOnBoard`) e Hero sem flush/nuts, em SRP HU de origem RFI/VS_OPEN call: Check grátis, Call até 20% do pote com `f$SRPStrongMade`, Call até 10% com `f$SRPTopGood`, Fold nos preços maiores. Thresholds não calibrados em EV. 7 testes focados.
- **Status:** M08 PARTIAL; 0/14 capacidades R10d VERIFIED, G1/G6 operacionais pendentes, G2-a HOLD; não é release. OH-G1G6-1 captura somente fórmula anterior ISODEF-1, sem certificação transferível.
