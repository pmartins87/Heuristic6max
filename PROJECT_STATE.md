# Estado atual — Heuristic6max
**Data:** 20/11/2026 | **Checkpoint:** RFI-MVP 6-max em OpenPPL sobre v0.6.1 | **Estado estratégico:** G2-a HOLD / não operacional.

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
