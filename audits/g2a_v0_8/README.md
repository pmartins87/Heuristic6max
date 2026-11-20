# G2-a v0.8 — composição de defesa VS_3BET e sensibilidade a terceiros

**Data: 20/11/2026. Auditoria incremental, sem editar nenhuma política de pôquer.** Base: `gto6_heuristic_v0_6_1` (124 testes), v0.7 (7 testes), e 11 testes novos (v0.8). Portanto, 142 testes independentes executados localmente. **Isto não demonstra EV, GTO ou lucratividade.**

## O que foi calculado

1. Para cada classe do Hero: probabilidade de RFI, posterior da classe condicionado ao RFI e à 3bet do adversário, exclusão de cartas físicas, contribuição em pontos percentuais para FOLD, CALL e 4BET. `DEFENSE_CLASSES_8_v0_8.csv` cobre os oito confrontos críticos, não muda os ranges.
2. Agrupamento em nove famílias para todos os 15 nós; decomposição de fold/call/4bet e pot odds **imediatas** de call. `DEFENSE_FAMILIES_15_v0_8.csv`.
3. Sensibilidade de custo da 3bet do agressor à interferência de jogadores posteriores (cold actions) sob o experimento **isolado, zero-equidade, simulado** da v0.7. `COLD_ACTION_SENSITIVITY_15_v0_8.csv`.
4. As 12 classes mais influentes na massa de folds de cada confronto crítico. `TOP_FOLD_CLASSES_8_v0_8.csv`. **Rankings são de contribuição à frequência, não ranking de mãos que deveriam dar call.**

### Identidade da distribuição por classes

Para uma mão física `h` do Hero, a massa condicional não-normalizada é:

`M(h) = P(RFI | h) × Σ_{v sem cartas comuns com h} P(vilão 3bet | v)`.

Normalizar `M(h)` para todas as 1.326 combinações do Hero e agregar às 169 classes. Depois multiplicar pelas frequências FOLD/CALL/4BET já existentes. Os totais reproduzem a v0.6.1 em **15/15** nós; nenhum parâmetro estratégico é ajustado.

### Resultados concretos

No confronto **HJ abre e CO dá 3-bet**, o Hero desiste 77,5377% das vezes no modelo, com estas contribuições à massa total:

- **23,2205 pontos percentuais** são mãos suited fora da classe de broadways/Ax; todas recebem FOLD 100%.
- **11,2818 pp** são pares baixos (22–66); todos recebem FOLD 100%.
- **9,2929 pp** são broadways offsuit não-Ax; todos recebem FOLD 100%.
- **14,3167 pp** são Ax offsuit, de uma massa total de 17,6364 pp dessa família.

Somadas, essas quatro famílias representam **58,1119 pp** das desistências. Isso é uma evidência **de concentração mecânica do fold**, não prova de que qualquer uma dessas mãos tenha call de EV positivo ou de que o RFI esteja necessariamente errado. Exemplo de revisão futura: HJ abre A9o e KJo com 100% na base RFI, mas desiste de ambas em 100% frente à 3bet CO; é preciso avaliar **as duas decisões em conjunto**, com rake e tamanho das apostas.

No spot **LJ vs HJ**, AJo, KQo e ATo contribuem ~4,55, 4,50 e 4,49 pp para folds. Esses folds podem ser estrategicamente razoáveis; a priorização de análise não significa recomendação de call.

### Fronteira de cold actions no experimento zero-equidade

Se `f = P(Hero fold | RFI, 3bet do adversário)`, `P` é pote anterior e `R` é custo adicional da 3bet, então, ao introduzir `q=P(nenhum terceiro intervém)` sob a hipótese **extra** de independência entre eventos:

`EV_fictício(q) = q f P − (1 − q f) R`.

Para que permaneça acima de zero, `q ≥ [R / (P+R)] / f`. Esse `q` **não foi medido no ambiente real**. A probabilidade por jogador informada é uma tradução hipotética que assume independência e taxas idênticas dos jogadores ainda por falar; não é estimativa observacional.

| Spot | Jogadores ainda por falar | q mínimo para EV contrafactual >= 0 | Taxa máxima *por jogador* se independentes |
|---|---:|---:|---:|
| LJ-HJ | 4 | 88,20% | 3,09% |
| HJ-CO | 3 | 85,98% | 4,91% |
| HJ-BTN | 2 | 87,12% | 6,66% |
| CO-BTN | 2 | 93,83% | 3,14% |
| BTN-SB | 1 | 99,51% | 0,49% |
| SB-BB | 0 | impossível (q exigido 112,33%) | não aplicável |

Quando não existem jogadores a agir após o 3bettor, não há cenário de taxa hipotética de cold action; células de sensibilidade para q<100% ficam vazias no CSV.

**Interpretação cautelosa:** a conclusão positiva da v0.7 para BTN-SB é tão marginal que uma pequena chance de interferência do BB pode invertê-la; nos outros cenários há limites distintos. Não interpretar como prova de ausência ou presença de exploração real.

## Reproduzir a partir da raiz do repositório

```sh
python -m unittest discover -s audits/g2a_v0_8 -p 'test_*.py' -q
python audits/g2a_v0_8/defense_composition.py
```

Confirmar que os quatro CSVs regenerados não diferem dos arquivos rastreados no Git. **11 testes novos**, incluindo conservação exata de massa, coincidência com agregados da v0.6.1, classificação, pot odds, contagem de terceiros, sinais do contrafactual, cobertura dos oito nós e imutabilidade dos três CSVs estratégicos.

## Decisão / gate

**Manter G2-a HOLD.** O principal suspeito agora é a combinação de RFI relativamente amplo com resposta estreita às 3-bets em determinadas classes; não há evidência suficiente para transferir essas mãos de FOLD para CALL ou 4BET. Priorizar auditoria econômica RFI-versus-3bet (rake/cap e sizings), comparação individual de mãos em árvores equivalentes, e replays reais em ambiente sem apostas. **Não iniciar VS_4BET/G2-b nem editar os três ranges-base.**

## Nota de reprodução e correção CI

Uma primeira execução CI (Python 3.11) identificou ordem distinta nas linhas de classes de massa praticamente idêntica à gerada no Python 3.13. **Não houve mudança no cálculo nem nas decisões**: os arquivos passaram a usar ordenação por chave de massa arredondada em 12 casas, seguida pelo identificador da mão. Acrescentado teste de desempate determinístico. Este ajuste mantém 15/15 agregados e permite reproduzir CSVs entre versões de Python.
