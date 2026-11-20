# G2-a v0.9 — HJ vs CO: fronteiras RFI/VS_3BET e cenários econômicos

**Data:** 20/11/2026. **Somente auditoria incremental.** O motor e as políticas continuam em `gto6_heuristic_v0_6_1/`; esta pasta NÃO modifica ranges, sizes nem ações, e NÃO é solver ou sistema operacional.

## Base lida e reproduzida
- HJ abre 2,5 BB, CO aplica 3-bet para 8 BB, blinds inativos SB 0,5 / BB 1, sem ante e sem caller no ramo estudado.
- A política HJ/CO responde, **condicionado a RFI+3bet e card removal**, com FOLD **77,53771778%**, CALL **14,03919921%** e 4BET **8,42308301%**. Igualdade conferida contra auditoria v0.6.1.
- A9o, KJo, AJo, KQo, ATo, AQo, pares 22–66, JTs e T9s são exemplos de RFI aberto e FOLD puro na resposta a 3-bet. A5s possui 4-bet de blefe mista; TT recebe CALL puro.
- A presença da mão no ranking de fold **NÃO** implica que o fold é errado nem que call/4-bet seja lucrativo.

## Arquivos reprodutíveis
- `hj_co_frontier.py`: álgebra de preço de call e 4-bet, posterior com bloqueio físico e contrafactuais por classe.
- `test_hj_co_frontier.py`: **11 testes** (massas 169 classes, consistência com a baseline, probabilidade de 3bet por enumeração física, cenários e preservação das três tabelas estratégicas).
- `HJ_CO_169_CLASS_SCREEN_v0_9.csv`: todas as 169 classes, P(RFI), probabilidade heurística de 3-bet do CO dadas as cartas Hero (uniformidade hipotética da mão do CO), posterior, ações e contribuição de FOLD.
- `HJ_CO_CANDIDATE_COUNTERFACTUALS_v0_9.csv`: para 15 classes selecionadas, modelos de cortar 50% ou 100% do RFI ou transferir **25 p.p. do FOLD** para CALL/4BET se houver massa; apenas demonstração de como mudam os agregados.
- `HJ_CO_PRICE_FRONTIER_v0_9.csv`: 3 sizings × 3 hipóteses artificiais de rake × 4 hipóteses de realização de equidade = **36 cenários**, sem equidade estimada nem EV real.
- `DECISION_NOTE.md`: recomendações e critérios de alteração.
- `AUDIT_SHA256SUMS.txt`: manifesto de integridade dos outros arquivos desta auditoria.

## Preço matemático no cenário base, não GTO

Com HJ 2,5 BB, CO 8 BB e blinds 1,5 BB: pote na vez do Hero = **12 BB**, custo adicional do call = **5,5 BB**, pote depois do call = **17,5 BB**.

Para um modelo simplificado de showdown sem novas apostas:

`EV_call_toy = raw_equity × realization_factor × (17.5 − rake_model) − 5.5`.

Logo, exigência de **equidade bruta teórica**, por exemplo:

| Rake hipotético | Realização 100% | Realização 75% |
|---|---:|---:|
| Sem rake | 31,43% | 41,90% |
| 5% com teto 3 BB (0,875 BB neste pote) | 33,08% | 44,11% |
| 8% com teto 3 BB (1,4 BB neste pote) | 34,16% | 45,55% |

Essas linhas **não** são parâmetros da plataforma-alvo, nem simulam mãos, fold equity, turns, rivers ou futuros pagamentos. Um `realization_factor` arbitrário não representa uma previsão medida de EQR. Mais rake ou menor realização aumenta a equidade necessária; isso **não permite inferir qual mão passar de FOLD para CALL**. Os modelos não contemplam cold action dos jogadores após CO, ou rake exato sobre futuros potes.

4-bet normal estimada a **21,2 BB**, logo arrisca mais **18,7 BB**; no experimento de blefe com equidade zero, demais jogadores desistindo e perda integral dos 18,7 BB se alguém continuar, a porcentagem necessária de todos desistirem é **60,91%**. Não é uma recomendação de 4-bet e não corresponde ao EV real.

## Contrafactuais individuais: concentração, não qualidade

A9o compõe **3,794%** da massa após RFI+3bet e é FOLD puro na baseline.
- **Cortar A9o do RFI** (somente no modelo): fold agregado passa de 77,54% para cerca de **76,65%**, e a frequência total de RFI cai **0,905 p.p.** no universo de 1.326 combinações iniciais. Isso pode piorar EV de steals/aberturas; nenhuma conclusão de valor é possível.
- **Transferir 25 p.p. de FOLD de A9o para CALL**: fold agregado hipotético cairia para cerca de **76,59%**, **sem prova** de que A9o possua equidade realizada para o call.
- O mesmo cálculo se aplica a AQo, AJo, KJo, KQo e às outras classes. Seleção de ação precisa ser justificada por EV da mão e contexto de rake/range adversário, não por melhorar uma porcentagem global.

## Limitações e decisão

1. A probabilidade de 3-bet condicionada às cartas da mão é derivada da política heurística `VS_OPEN` do projeto, supondo mão do CO uniformemente distribuída entre as combinações disponíveis, não de observação de um adversário real.
2. A parte contrafactual mantém fixos os demais ranges, respostas do CO e ações de jogadores posteriores — mudança de política alteraria toda a árvore.
3. A derivação com rake usa um **pote terminal artificial**, não uma árvore pós-flop. A decisão de abrir uma mão (RFI) não pode ser julgada pelo seu fold pós-3bet isoladamente.
4. Não há dados de rake/cap reais, frequências de 3-bet observadas, equidade contra range, EQR validada, EV do open ou EV de call/4bet. Sem isso, alteração de estratégia seria prematura.

**Decisão do gate:** manter G2-a **HOLD** e G2-b/VS_4BET bloqueado. Preservar as três tabelas estratégicas exatamente como estavam. Próximo trabalho: selecionar uma configuração de rake/cap/sizing-alvo, computar equity por classe contra o range adversário com método verificável e aferir realização/EV sob replays ou simulação estruturada.

## Reprodução

Na raiz do repositório:

```bash
python scripts/check_repository.py
python -m unittest discover -s audits/g2a_v0_7 -p 'test_*.py' -q
python -m unittest discover -s audits/g2a_v0_8 -p 'test_*.py' -q
python -m unittest discover -s audits/g2a_v0_9 -p 'test_*.py' -q
python audits/g2a_v0_9/hj_co_frontier.py
cd audits/g2a_v0_9 && sha256sum -c AUDIT_SHA256SUMS.txt
```

A CI deve registrar **153 testes** (124 + 7 + 11 + 11) e diferenças nulas nos três CSVs gerados. A contagem não comprova qualidade estratégica.
