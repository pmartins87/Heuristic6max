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