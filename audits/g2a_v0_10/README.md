# G2-a v0.10 — equidade pré-flop HJ vs CO com 3-bet modelada

**Checkpoint:** 20/11/2026. **Somente auditoria.** Base do jogo inalterada: `gto6_heuristic_v0_6_1/` (RFI, VS_OPEN e VS_3BET continuam DRAFT). Não utilizar como estratégia operacional nem como prova de GTO ou de EV positivo.

## Fontes e proveniência

1. **Ranges de HJ/CO:** fonte de verdade [VS_OPEN](../../gto6_heuristic_v0_6_1/vs_open_reference.py) e [VS_3BET](../../gto6_heuristic_v0_6_1/vs_3bet_reference.py). O modelo adversário não representa um oponente real observado.
2. **Referência independente de showdown:** arquivo `PreFlopEquities.zip`, previamente fornecido ao projeto, contendo `PreFlopEquities.txt` com 1.624.350 pares **ordenados** de duas mãos físicas distintas; cada confronto tem uma equidade percentual com **duas casas decimais**. O código verifica: formato, ausência de sobreposição de cartas, cobertura de todos os confrontos físicos ordenados, ausência de duplicatas, existência do confronto reverso e equidades complementares. Essas verificações passaram para o ZIP analisado.
3. **SHA-256 do ZIP fornecido:** `52a0a87174b0d7cabd5b16fe43387b0807a6abd036e5a61c1aafbc008ecf50c2`; **SHA-256 de `PreFlopEquities.txt`:** `9dd539e2720010684d0006981207489e4f753b1d628f7e0443003b2c7f3e6c9f`.
4. **Restrição de distribuição:** a proveniência autoral e a licença do ZIP não foram estabelecidas; o arquivo bruto **não foi publicado** no repositório público. Publicamos o código, o digest do arquivo de entrada e os resultados agregados derivados (169 linhas). Portanto, a reprodução *exata a partir dos dados originais* exige uma cópia licenciada/autorizada do ZIP idêntico; a reprodução independente *aproximada, apenas com o GitHub* é possível via Monte Carlo Python stdlib publicado aqui.

A origem algorítmica da tabela de confrontos não foi certificada. Não a chamar de solver nem de fonte GTO; os valores foram adicionalmente confrontados com um avaliador de 7 cartas via Monte Carlo implementado separadamente.

## Metodologia

Para cada classe de mão física do Hero `h`, confrontamos todas as possíveis mãos físicas do vilão `v` sem cartas comuns. Calculamos:

`Eq_classe = sum_{h da classe} sum_{v disjunto de h} P(3bet_CO|v) * EquityTabela(h,v) / sum_{h da classe} sum_{v disjunto de h} P(3bet_CO|v)`.

A probabilidade de RFI do HJ é a mesma para todos os combos físicos de uma classe; condicionada à classe já aberta, ela cancela na fração. Para a distribuição **entre classes**, a probabilidade RFI ainda precisa ser considerada (ferramentas v0.6–v0.9 já fazem isso). A tabela usa equity do Hero **incluindo metade dos empates**, não frequência de vitória sem empate.

O modelo do vilão é a 3-bet definida no VS_OPEN contra HJ, não uma distribuição observada. Sem resolver a árvore pós-flop, a equidade bruta pré-flop **não é a equidade realizada**. Rake, stack futuro, possibilidade de fold no flop, apostas posteriores, cold calls e cold 4-bets ficam fora da medição.

## Valores de classes prioritárias

| Mão | Equity bruta vs CO 3bet |
|---|---:|
| AQo | 41,3101% |
| TT | 44,0217% |
| 99 | 41,6948% |
| 66 | 41,3177% |
| 22 | 38,4830% |
| AJo | 35,6951% |
| A9o | 32,6490% |
| KJo | 32,3099% |
| KQo | 32,8275% |
| JTs | 33,1567% |
| A5s | 36,6005% |

A tabela completa está em `HJ_CO_EQUITY_169_REFERENCE_v0_10.csv`. O check separado `HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv` usa 50.000 amostras **determinísticas** por classe candidata; o maior desvio entre os 15 valores do Monte Carlo e a referência agregada foi **0,4597 ponto percentual**. Isso valida parcialmente consistência física/avaliação das mãos, não a licença nem a metodologia da tabela.

## Limites do modelo de call

No caso-base da v0.9, HJ abriu 2,5 BB e CO 3-betou para 8 BB. HJ precisa colocar 5,5 BB em pote final 17,5 BB: **31,4286% de equity realizada mínima sem rake**, em um modelo hipotético de showdown terminal. Com `realization_factor` arbitrário de 75% e rake artificial de 5% sobre o pote terminal, a equity bruta limiar subiria para **44,110%** aproximadamente. **Esses fatores não foram medidos e não modelam EV real.**

Exemplo: AQo tem 41,31% de equity bruta, mas ainda recebe fold puro no ramo atual. A equity bruta excede o preço sem rake com realização perfeita, porém fica abaixo do preço ilustrativo com EQR 75% e rake 5%; **não devemos converter AQo para call por causa desse resultado**. Para pares baixos, 38–41% de equity também não incorpora set-mining, reverse implied odds nem fold equity pós-flop. Não há uma conclusão automática de EV.

## Arquivos

- `equity_audit.py`: leitura opcional do ZIP fornecido, validação integral, cálculo agregado 169 classes; avaliador independente de 7 cartas e Monte Carlo determinístico, implementados na biblioteca padrão.
- `HJ_CO_EQUITY_169_REFERENCE_v0_10.csv`: agregados derivados do arquivo de referência para 169 classes, **não o dataset bruto**.
- `HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv`: validação aproximada independente, 50 mil amostras por candidata.
- `test_equity_audit.py`: **10 novos testes**; conferência de combinatória, fonte, evaluator e integridade das tabelas de estratégia.
- `DECISION_NOTE.md`: justifica manutenção do HOLD; `AUDIT_SHA256SUMS.txt`: hashes dos arquivos deste checkpoint.

## Reprodução (sem dataset privado)

```bash
python -m unittest discover -s audits/g2a_v0_10 -p 'test_*.py' -q
python audits/g2a_v0_10/equity_audit.py --mc --samples 50000 --output audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv
cd audits/g2a_v0_10 && sha256sum -c AUDIT_SHA256SUMS.txt
```

Para recálculo **exato da referência original** usando uma cópia autorizada do ZIP, a partir da raiz do repositório:

```bash
python audits/g2a_v0_10/equity_audit.py --reference-zip /caminho/autorizado/PreFlopEquities.zip --output audits/g2a_v0_10/HJ_CO_EQUITY_169_REFERENCE_v0_10.csv
```

Não há instalação de bibliotecas externas. A CI GitHub executa os 124 testes base +7 (v0.7) +11 (v0.8) +11 (v0.9) +10 (v0.10) = **163 testes**, confere o CSV de Monte Carlo reproduzido, a estrutura do CSV de referência e os hashes do checkpoint. **A CI pública não roda o ZIP privado.**

## Recomendação / Gate

**G2-a continua HOLD**. Preservar RFI/VS_OPEN/VS_3BET e o roadmap original. Próximo passo: construir aproximação de EV de call/4-bet com rake/cap parametrizado, cenários de equidade realizada, posição e adversários restantes; obter calibração pós-flop ou replays reais antes de modificar qualquer frequência. G1 permanece aberto e G2-b VS_4BET permanece bloqueado.
