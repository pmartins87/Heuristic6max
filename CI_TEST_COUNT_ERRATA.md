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

## ISODEF-1 — contagem verificada na CI (21/11/2026)

| Referência | Commit de PR | Execuções de testes (`Ran N tests`) | Testes deduplicados por suíte | Suítes |
|---|---|---:|---:|---:|
| [ISODEF-1 aprovado](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038) | `c0de8d25bad2ff9869335ab3efe2636a2a3eeec3` | **573** | **561** | **29** |

Os 29 registros `Ran N tests` no log de CI somaram 573 execuções. A suíte do benchmark R10d com 12 testes roda duas vezes: 573 − 12 = **561 testes deduplicados por suíte**, aumento de 21 frente aos 552/540 de BLISO-2. A reconstrução OpenPPL, preservação do ancestral, relatório R10d e manifestos SHA256 passaram. **Não** são 561 decisões de poker, nem replays OpenHoldem; o gate 14/14 ainda bloqueia release.

## OH-G1G6-1 — controle de contagem factual (21/11/2026)
| Referência | Commit do PR | Execuções (`Ran N tests`) | Deduplicados por suíte | Suítes |
|---|---|---:|---:|---:|
| [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886) | `c0a1eed16fe17212e1cca1d4c117c268d280e55a` | **599** | **587** | **30** |
Os **30** registros de testes no log do job `136719229320` somam **599**; uma suíte R10d de 12 testes é executada duas vezes (599 − 12 = **587** por deduplicação de suíte). Ganho de **26 testes**, ante 573/561 em 29 suítes no ISODEF-1. Os 26 são verificações sobre evidências sintéticas e guardas da auditoria, não replays OH nem 26 decisões estratégicas. **G1/G6 e 14/14 gates R10d não foram promovidos**.
