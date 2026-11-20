# Estado atual — Heuristic6max
**Data:** 20/11/2026 | **Checkpoint:** auditoria v0.11 de fontes sobre v0.10 sobre v0.6.1 G2-a | **Estado estratégico:** HOLD / não operacional.

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
