# CI_TEST_COUNT_ERRATA — 20/11/2026

## Origem dos números
Os totais antigos de **434** e **472** foram extrapolados de etapas de desenvolvimento, sem considerar todas as suítes realmente executadas pelo workflow. São números errados e não devem ser citados como contagem de execução ou de testes exclusivos.

A verificação foi feita lendo **os logs reais dos jobs GitHub Actions**:

| Referência | Commit | Execuções de testes (`Ran N tests` somadas) | Testes distintos | Número de suítes executadas |
|---|---|---:|---:|---:|
| [Rodada anterior](https://github.com/pmartins87/Heuristic6max/actions/runs/44847881105) | `2b0d37318756a3700a6333fb817225cbfb6abda1` | 483 | 471 | 23 |
| [Rodada MWT3/MLIMP2/P3BMW1](https://github.com/pmartins87/Heuristic6max/actions/runs/44849323978) | `ae4ed3987833a38fa793e1fc6ea1eb66834750d6` | **521** | **509** | 26 |

A CI chama a **mesma suíte** `benchmarks/r10d_floor/test_comparison.py` com 12 testes em duas etapas distintas do arquivo [verify.yml](.github/workflows/verify.yml). Para a contagem de testes distintos, subtraem-se 12 da soma de execuções. Fora essa duplicação deliberada pelo workflow, não foram identificados testes idênticos entre suítes por este procedimento de contagem. Portanto, `509` é a contagem deduplicada por suíte, não um inventário global de funções de teste semanticamente distintas.

## Efeito sobre o projeto

- **38 novas verificações** (+14 MWT3, +12 MLIMP2, +12 P3BMW1).
- Todos os resultados do [workflow 44849323978](https://github.com/pmartins87/Heuristic6max/actions/runs/44849323978) foram **success**.
- **Nenhum chart, range, regra de ação ou .oppl foi modificado para esta errata.**
- A compatibilidade no executável OpenHoldem continua pendente, e o critério obrigatório de superar funcionalmente o DeepCrusher_R10d continua **NOT MET** (14 famílias ainda não verificadas).
- Para checkpoints futuros, publicar **execuções de teste**, **testes deduplicados por suíte**, **hash do commit** e **link da execução** separadamente. Nunca extrapolar uma contagem por soma histórica desatualizada.

## Verificação
Consultar os logs dos jobs e as duas ocorrências de `python -m unittest discover -s benchmarks/r10d_floor -p 'test_*.py' -q` no workflow. Esta errata substitui especificamente os totais 434/472 das notas anteriores, mas não apaga esses checkpoints históricos.

## Novo checkpoint ISO-1 — CI verificada (20/11/2026)

| Referência | Commit | Execuções de testes (`Ran N tests`) | Testes distintos por deduplicação de suíte | Número de suítes |
|---|---|---:|---:|---:|
| [ISO-1 aprovada](https://github.com/pmartins87/Heuristic6max/actions/runs/44853164836) | `142c00eb036f1283253c2a7119798d77ef3d7540` | **534** | **522** | **27** |

Recontagem diretamente do log do job [44853164836](https://github.com/pmartins87/Heuristic6max/actions/runs/44853164836): 27 registros de `Ran N tests` somam 534 execuções. A suíte R10d de 12 testes continua intencionalmente executada duas vezes, portanto 534 − 12 = 522 por deduplicação de suíte. São **13 testes adicionais** à baseline 521/509, sem apagar checkpoints históricos. O teste de alteração de fonte, a regeneração e os manifestos SHA-256 passaram na mesma execução. Isso **não** valida código no executável OpenHoldem nem altera o gate 14/14.

## BLISO-2 — contagem auditada (20/11/2026)

| Referência | Commit | Execuções de testes (`Ran N tests`) | Deduplicados por suíte | Suítes |
|---|---|---:|---:|---:|
| [BLISO-2 aprovado](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418) | `8da515beed4f522fb5c41c9779e811e24e617806` | **552** | **540** | **28** |

Os 28 registros `Ran N tests` do job 136704854736 somaram 552; a suíte R10d é executada duas vezes, com 12 verificações repetidas, totalizando 540 por deduplicação de suíte. São +18 testes frente a ISO-1 (534/522). O build OpenPPL, integração, manifestos e benchmark passaram. Contagens são estáticas: sem prova de EV, runtime OH ou superioridade R10d.
