# G2-a — Auditoria condicional VS_3BET v0.6 (20/11/2026)

**Natureza:** verificação matemática dos **ranges heurísticos existentes**. Não é solver, calibração GTO, alteração de estratégia ou liberação operacional.

## Problema da medição anterior
A v0.5 media a ação do Hero ponderando `P(RFI|classe do Hero)`, mas **não condicionava à ocorrência efetiva de uma 3-bet pelo adversário**. Mãos fortes do Hero removem combinações de valor do range de 3-bet adversário, causando viés em agregados observados no nó.

## Correção de contabilidade — sem alterar decisões
Considere uma mão física `h` do Hero (2 cartas), uma mão física `v` do vilão, e `a(h)` sua ação mista VS_3BET. Para um confronto de posições:

`Peso(h) = P(RFI | classe(h)) × Σ_{v disjunto de h} P(3bet | classe(v), posições)`.

A frequência condicional da ação `A`, **no modelo interno heurístico**, é:

`P(A | RFI, 3bet) = Σ_h Peso(h) × P(A | classe(h)) / Σ_h Peso(h)`.

As 1.326 combinações físicas são enumeradas. Para cada par de cartas do Hero, o somatório de vilão disjunto é calculado por inclusão-exclusão: `Total3bet - MassaCarta1 - MassaCarta2 + MassaParExato`. Os pesos de 3-bet provêm de `vs_open_reference.RANGES` para o mesmo confronto; não há modelo de adversário real nem estimativa de EV. O restante dos jogadores é marginalizado como cartas desconhecidas.

`test_vs3_blocker_audit_v0_6.py` compara a inclusão-exclusão a uma enumeração dupla direta de todas as combinações do vilão em três confrontos e quatro mãos físicas do Hero; verifica 169 classes/1.326 combos, todas as probabilidades e a faixa de shares de blefe.

## Resultado quantitativo
- 15 confrontos analisados; nenhum foi alterado.
- 4-bet condicional cai entre **0,409 e 1,766 pontos percentuais** vs agregado da v0.5 (diferenças arredondadas).
- LJ vs HJ: 12,232% → 10,466%; CO vs BTN: 8,934% → 8,290%; BTN vs SB: 6,241% → 5,813%; SB vs BB: 7,792% → 7,382%.
- Dos oito confrontos previamente marcados `MAJOR_REVIEW`, sete apresentam distância absoluta superior a 8 p.p. dos benchmarks antigos após a nova medição; BTN vs SB apresenta 6,09 p.p. Os benchmarks **não têm rake/árvore equivalentes**; portanto a distância não é erro comprovado nem alvo a copiar.
- As frequências de blefe nas 4-bets são recalculadas com a mesma ponderação física, mas **não representam misturas GTO ótimas**.

## Evidências entregues
- `G2A_VS3_BLOCKER_15_NODES_v0_6.csv` — ações antigas, ações condicionadas e novos shares de blefe.
- `G2A_VS3_BLOCKER_TOP_HANDS_v0_6.csv` — pesos de classes após o evento de 3-bet.
- `G2A_MAJOR_REVIEW_8_NODES_v0_6.csv` — gaps comparativos das oito pendências.
- `vs3_blocker_audit_v0_6.py` e `test_vs3_blocker_audit_v0_6.py` — reprodutibilidade.

## Decisão e gates
**Manter HOLD G2-a**, preservar RFI/VS_OPEN/VS_3BET e não iniciar VS_4BET. Para decidir mudança estratégica: (a) definir rake e sizings alvos, (b) avaliar composição individual e efeitos de bloqueio de adversário por posição, (c) obter comparação com premissas equivalentes ou EV defensável, (d) adicionar testes de regressão de ação final. O G1 continua aberto até replays reais, obtidos apenas em ambiente de teste sem apostas.
