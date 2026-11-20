# G2-a v0.7 — Pressão de 3-bet isolada e investigação de subdefesa

**20/11/2026. Diagnóstico independente de solver, sem mudança na política do Hero.**

## Evidência matemática

A v0.6.1 já recalculava `P(ação Hero | RFI, 3bet do vilão)`. Nesta auditoria, condicionamos **a cada combinação física de duas cartas do vilão**, excluindo as duas cartas do range inicial do Hero. A probabilidade condicional do Hero desistir é calculada com inclusão-exclusão nas 1.326 combinações físicas. Agregamos as combinações de vilão usando `P(3bet | mão do vilão) × Massa(RFI Hero | cartas do vilão removidas)`, reproduzindo os resultados de `vs3_blocker_audit_v0_6.py` em todos os 15 nós.

Para um *experimento isolado* em que os jogadores atrás **sempre desistem**, a 3-bet adversária é colocada com `R` BB adicionais (descontado blind já postado) para tentar capturar `P` BB de pote existente. Na hipótese **artificial** de perder integralmente `R` sempre que o Hero continua (zero equidade, sem valor futuro), a esperança da 3-bet é:

`EV_isolado_zeroequidade = P(Hero fold) × P - (1 - P(Hero fold)) × R`.

Ponto de equilíbrio: `P(Hero fold) = R / (R + P)`.

**Importante:** isso **não é EV real** nem comprova que uma 3-bet será lucrativa no jogo verdadeiro: há jogadores ainda por falar em vários nós, outros potes posteriores, rake, equidade do vilão, comportamento dos blinds, 4-bets e decisões posteriores. Uma bandeira positiva significa **risco de subdefesa sob a hipótese explícita**, não licença para alterar ranges automaticamente.

## Resultados mais relevantes (15 nós)

| Opener vs 3bettor | Fold do Hero (modelo) | Break-even (vilão, equidade zero) | EV contrafactual (BB) |
|---|---:|---:|---:|
| LJ-HJ | 75,59% | 66,67% | +1,071 |
| LJ-CO | 74,62% | 66,67% | +0,954 |
| LJ-BTN | 74,48% | 66,67% | +0,938 |
| HJ-CO | **77,54%** | 66,67% | **+1,305** |
| HJ-BTN | 76,53% | 66,67% | +1,183 |
| CO-BTN | 71,05% | 66,67% | +0,526 |
| BTN-SB | 71,26% | 70,91% | +0,048 (limítrofe) |
| SB-BB | 60,76% | 68,25% | −0,944 |

Nos oito confrontos originalmente em `MAJOR_REVIEW`, sete apresentam pressão positiva nesse cenário contrafactual; SB-BB não. Nos 15 nós, sete aparecem positivos (os mesmos sete acima). Esses cálculos consideram apenas os sizings *fixos* do modelo v0.6.1; com tamanho de 3-bet diferente, o resultado muda.

**Nota sobre posição e jogadores restantes:** LJ vs HJ, CO, BTN e BTN vs SB têm ações possíveis de outros jogadores. Não considerar o dinheiro nem a ação desses jogadores seria incorreto fora da hipótese de isolamento. SB-BB é o confronto que mais se aproxima de um nó realmente sem terceiros restantes. A pressão positiva de BTN-SB (0,048 BB) é pequena e não deve ser classificada como evidência sólida de exploração real.

## Arquivos

- `pressure_audit.py` — cálculo reproduzível em Python (stdlib + fontes v0.6.1).
- `3BET_PRESSURE_ALL_15_v0_7.csv` — todos os confrontos, com pot, risco, threshold e média condicional.
- `3BET_PRESSURE_HANDS_8_v0_7.csv` — participação e probabilidade de fold por cada classe física elegível do vilão nos 8 nós em auditoria.
- `test_pressure_audit.py` — regressões: conservação de massa por 15 nós, confrontos, card removal por enumeração direta, pot odds, preservação da política e classes por mão.

## Reprodução

A partir da raiz do repositório:

```bash
python audits/g2a_v0_7/pressure_audit.py
python -m unittest discover -s audits/g2a_v0_7 -p 'test_*.py' -q
python scripts/check_repository.py
```

Gera CSVs no diretório da auditoria; os valores devem coincidir com os arquivos commitados (não escreva por cima de resultados verificáveis sem registrar diff). **7 novos testes**, além dos 124 da v0.6.1.

## Decisão para o gate G2-a

**Manter HOLD estratégico**, preservar os 3 ranges-base v0.4. A evidência nova muda a *prioridade de revisão*: em vez de mirar apenas diferenças de frequência de 4-bet em benchmarks não comparáveis, investigar primeiro a **defesa combinada de 4-bet + call** e a taxa de fold contra tamanho da 3-bet, especialmente em HJ-CO, HJ-BTN, LJ-HJ, LJ-CO, LJ-BTN e CO-BTN. Antes de qualquer edição de range, obter configurações econômicas concretas (rake/cap), verificar variações de sizing e a atuação dos jogadores atrás, fazer uma proposta explícita de revisão com testes e medir o impacto. Ainda faltam replays reais em ambiente de teste.
