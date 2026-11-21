# Manifesto de versões (20/11/2026)

| Versão | SHA-256 do ZIP local | Fonte no GitHub |
|---|---|---|
| v0.1 | 92a0f3a847d0eb62d10e35d6d6aa5be45a51b375e72f430168ce53c72a888397 | Histórico em v0.5/v0.6 |
| v0.2 | d864c3f9dd2c7699dcba17c9b27c6c3f5cc87f0def89fa845b4cec7a912abf52 | Histórico em v0.5/v0.6 |
| v0.3 | ec6ca7de7a10893e9dbb8bc18baabd3404f69e0435b02af755e0229650b6d552 | Histórico em v0.5/v0.6 |
| v0.4 | 6086ccc8b7b4aae583d831287643cfc8f6330769ab96c5d901fdefd63279e227 | Baseline preservada em v0.5/v0.6 |
| v0.5 | 7b036634896c560fbc7e4a1794f981860fdd9a065bf3161abb0698b6bf97022a | gto6_heuristic_v0_5/ — 51 arquivos |
| v0.6 | 0844f9758ed13ff063ad0c3aeab9b30298b1c0c5e4cfd3ef033f7d6cf70ae963 | gto6_heuristic_v0_6/ — 61 arquivos (errata de manifesto) |
| v0.6.1 | 2513b01af1498b7059c4eade7f0be1c9fe7fce4cb07fc3eef76e74ae80d29c32 | gto6_heuristic_v0_6_1/ — 66 arquivos (corrigido) |

**Importação v0.5:** commit 91bb2fdd3d1535f7746f7c39ecaddd98db9ebb72, 51 arquivos.  
**Importação v0.6:** commit 3bbfe3a753111013848e6157c78746e3f49f86d6, 61 arquivos.

Os hashes do ZIP servem à transferência local; não representam commits Git nem presumem que o ZIP esteja no GitHub. O repositório contém as árvores de arquivos texto completas. Cada pasta inclui SHA256SUMS.txt para validação dos arquivos do snapshot; a v0.6 inclui auditoria de preservação dos 51 arquivos-base v0.5.

**Status:** v0.6.1 teste local 124/124, mas **não operacional**. G1 aberto e G2-a HOLD.

**Correção v0.6.1:** commit a107afa05680c16ca5b0314ebdb892dca1b474af, snapshot com 66 arquivos e [ERRATA](gto6_heuristic_v0_6_1/ERRATA_v0_6_1.md).

## Auditoria incremental v0.7 — sem ZIP obrigatório
Localização versionada: [audits/g2a_v0_7/](audits/g2a_v0_7/). Contém script, 7 testes, relatório e dois CSVs. Base de execução imutável: v0.6.1 (66 arquivos). Esta é **versão de auditoria**, não versão operacional nem mudança de ranges. Esperado em CI: 124 testes baseline + 7 testes de auditoria, com diffs nulos nos relatórios regenerados.

## Auditoria incremental v0.8 — sem novo ZIP
- Diretório: [audits/g2a_v0_8/](audits/g2a_v0_8/); nove arquivos de auditoria, incluindo **AUDIT_SHA256SUMS.txt** sobre oito outros arquivos.
- Dependências versionadas: v0.6.1 (66 arquivos) e v0.7 (7 testes e auditoria). O v0.8 não substitui a baseline e não muda políticas.
- Reexecução esperada: 124+7+11 = **142 testes**, quatro relatórios CSV determinísticos, verificação SHA256 e CI verde.

## Auditoria incremental v0.9 — sem ZIP operacional
- Diretório GitHub: [audits/g2a_v0_9/](audits/g2a_v0_9/), **8 arquivos** incluindo fontes, 3 CSVs, README, decisão, 11 testes e manifesto SHA256.
- Snapshot estratégico dependente: v0.6.1, inalterado. Depende também de v0.8/v0.7; não é nova release operacional.
- CI esperada: 124+7+11+11 = **153 testes**, 3 CSVs determinísticos, SHA256 do audit e diff Git nulo. Sem alegar GTO/EV validado.

## Auditoria incremental v0.10 — não operacional
- Diretório GitHub: [audits/g2a_v0_10](audits/g2a_v0_10/), sete arquivos (motor, 10 testes, 169 equities derivadas, 15 checks MC, docs, hash-manifesto).
- SHA-256 do input externo PreFlopEquities.zip: 52a0a87174b0d7cabd5b16fe43387b0807a6abd036e5a61c1aafbc008ecf50c2. SHA-256 de PreFlopEquities.txt: 9dd539e2720010684d0006981207489e4f753b1d628f7e0443003b2c7f3e6c9f. O input bruto não é hospedado (licenciamento não estabelecido); somente cálculos derivados e método/fallback MC stdlib.
- CI esperada: 124+7+11+11+10=163 testes, CSV Monte Carlo regenerado de modo determinístico e manifesto verificado. Ranges v0.6.1 intocados, G2-a HOLD.

## Auditoria incremental v0.11 — gate de fontes, não operacional
- [audits/g2a_v0_11/](audits/g2a_v0_11/) inclui 7 arquivos: código, testes, registry JSON, CSV derivado, README, decisão, manifesto SHA256.
- Depende de baseline imutável v0.6.1 (100 BB, HJ 2,5 BB, CO 3bet 8 BB); não inclui charts proprietárias, nem fonte OpenPPL executável.
- CI esperada: **174 testes (124+7+11+11+10+11)**, CSV reproduzido sem diff e SHA256 validado. G2-a HOLD, G6 pendente.


## PORT-0 — checkpoint de portabilidade sem release operacional
[PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md), [portability/](portability/). Duas regras OPPL BTN RFI, sete testes em 3.042 estados; CI esperado 181 testes (174+7). Não altera snapshots estratégicos nem códigos anteriores. Não é compilação, integração ou teste do OpenHoldem.

## PORT-1 — checkpoint incremental, não release de bot
- [portability/port1](portability/port1/): sete arquivos com regras OpenPPL, interpretador de testes, gerador offline, 169 linhas de mapping, README, testes e manifesto SHA256.
- 15 testes incrementais; total esperado 196 (174+7+15). Teste de compatibilidade ainda estático; KJo permanece sem regra. Fonte estratégica v0.6.1 DRAFT não alterada; hashes históricos preservados.

## PORT-2 — artefato incremental de portabilidade estática (sem release operacional)
- [portability/port2/](portability/port2/): 7 arquivos versionados com fonte OpenPPL, interpretador, gerador, 19 testes, mapeamento, README e `PORT2_SHA256SUMS.txt` (hashes dos outros seis).
- Baseline imutável: v0.6.1, 66 arquivos. KJo RFI LJ 40/60 representado via `randomhand`, não convertido em ação pura.
- Reproduzir: gerador determinístico + `git diff`, 19 testes e `sha256sum -c PORT2_SHA256SUMS.txt`. Total CI esperado **215 = 196 + 19**. Não há teste OpenHoldem, não autoriza execução operacional.

## PORT-3 / RPL-0 — instrumento de replay (sem release operacional)
- [portability/port3/](portability/port3/) 7 arquivos (auditor, 27 testes, input e output sintéticos, README, .gitignore, `PORT3_SHA256SUMS.txt`).
- Base de decisão: `portability/port2/lj_rfi_mixed_port2.oppl` inalterada, v0.6.1 imutável. Nenhuma execução OpenHoldem reportada.
- CI: 215 testes anteriores + 27 = **242** previstos; reproduzir CSV sintético e hashes. Níveis de resultado NÃO incluem PASS operacional. G1 aberto, G2-a HOLD, G6 pendente.

## RFI-MVP 6-max — componente OpenPPL parcial, NÃO release operacional
- [portability/rfi_mvp/](portability/rfi_mvp/): 7 arquivos rastreados (OPPL 21 regras, gerador, interpretador, 12 testes, 845 linhas CSV, README e `RFI_MVP_SHA256SUMS.txt` sobre 6 arquivos).
- Depende de `gto6_heuristic_v0_6_1/` (66 arquivos, snapshot e políticas intactos). Há 5 mixes e limp da SB; não há dados novos de GTO/EV.
- CI esperada: **254 testes = 242 históricos + 12**, regeneração e diff nulo de OPPL/CSV, SHA256 dos artefatos. VS_OPEN/VS_3BET, fallback e OpenHoldem real ainda pendentes.

## VS_OPEN-MVP — componente pré-flop OpenPPL DRAFT (não release de bot)
- [portability/vs_open_mvp/](portability/vs_open_mvp/): **8 arquivos**: módulo OpenPPL de 121 regras/81 listas, combinado RFI+VS_OPEN de 142 regras, gerador offline, interpretador, 19 testes, CSV de 2.535 nós, README e `VS_OPEN_MVP_SHA256SUMS.txt` sobre 7 arquivos.
- Base estratégica v0.6.1 (66 arquivos) permanece historicamente intocada, com política VS_OPEN v0.3 DRAFT. Não incorporamos chart externa nem novo sizing de solver.
- CI prevista: **273 = 254 +19**; gera OPPL e CSV de modo determinístico, exige `git diff --exit-code` e manifesto SHA256. G1 sem replay, G2-a HOLD, G6 pendente; sem artefato operacional.

## VS_3BET-MVP — pacote incremental OpenPPL DRAFT (sem release operacional)
- [portability/vs_3bet_mvp/](portability/vs_3bet_mvp/) contém **8 arquivos**: gerador, interpretador, 23 testes, fonte VS3, fonte combinada, mapa 2.535, README e manifesto `VS3_MVP_SHA256SUMS.txt` dos outros sete.
- Baseline v0.6.1 intocada. 15 pares × 169; 888 alcançáveis e 1.647 com `NOT_REACHABLE_FROM_RFI`; 135 regras VS3 + 142 regras RFI/VS_OPEN = 277. Sem alteração no poker, sem integração testada.
- CI deve verificar: 254 testes anteriores + 23 = **277**; regeneração byte-idêntica dos dois OPPLs/CSV; SHA256 manifesto; `git diff` nulo. G1 aberto, G2-a HOLD, G6 pendente.

## G3 SRP-HU MVP — fonte OpenPPL, rascunho (20/11/2026)
- Diretório [portability/srp_hu_mvp/](portability/srp_hu_mvp/) inclui **7 arquivos**: README, regras pós-flop OPPL, arquivo combinado OPPL, interpretador offline, 18 testes, concatenador e manifesto SHA256 de seis conteúdos.
- Dependência direta: pré-flop `portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl`, preservado byte a byte. Baseline histórica v0.6.1 imutável.
- CI: 18 testes incrementais; validar SHA256, regenerar arquivo combinado com diff zero e executar todas suites anteriores. Não corresponde a release operacional e não houve teste no executável OpenHoldem.

## G3-HIST-v1 — módulo incremental de histórico (DRAFT)
- [portability/srp_history_v1/](portability/srp_history_v1/): 9 arquivos (overlay OpenPPL, pós-flop/arquivo completo gerados, intérprete, gerador, 18 testes, matriz 9 caminhos, README e `HISTORY_SHA256SUMS.txt`).
- Novo documento vivo [STRATEGY_ARCHITECTURE.md](STRATEGY_ARCHITECTURE.md) registra escopo de bot completo, fontes e gates.
- Nenhuma mudança em `gto6_heuristic_v0_6_1/`, `portability/vs_3bet_mvp/` e `portability/srp_hu_mvp/`. Pré-flop combinado original preservado; G3 novo tem 58 regras de ação e 24 helpers, 18 testes, total esperado no CI **295**.
- Sem replays reais ou certificado operacional OpenHoldem; não divulgar como bot pronto nem alegar winrate.

## G3-HIST-v2 — 36 trajetórias, snapshot DRAFT (não operacional)
- [portability/srp_history_v2/](portability/srp_history_v2/): 9 arquivos (OpenPPL autoral, gerador, 36 paths CSV, pós-flop e integrado, intérprete, 18 testes, README e `HISTORY_V2_SHA256SUMS.txt`).
- Base: `portability/srp_history_v1/`, `portability/vs_3bet_mvp/` e v0.6.1, **sem mudanças históricas**. 75 ações OPPL, 70 helpers, 36 trajetórias, os 9 estados antigos com paridade estática.
- Regenerar, checar `git diff`, testes e hashes conforme README. **Total esperado na CI 313**; sem build/paridade real OH, sem prova de EV ou de excelência estratégica.

## HIST-v3 — grafo histórico e correção de flags, DRAFT
- [portability/srp_history_v3/](portability/srp_history_v3/): 12 arquivos (2 OpenPPL completos, 2 fragmentos OPPL, enumerador, intérprete, gerador, 31 testes, 2 CSV, README e `HIST3_SHA256SUMS.txt`). As outras fontes históricas não mudaram.
- Universo estrutural novo: 484 caminhos legais (posição/role e até 4 raises), **não 484 ações estratégicas**; 3 colisões documentadas. Fonte de ação conserva 75 regras antigas e 10 helpers novos, 4 memórias `Set`. Pré-flop combinado imutável.
- Testes: 31 incrementais, **344 acumulados previstos**. Regenerar CSV/OPPL e verificar hashes no CI; testes de execução OH/alvo continuam inexistentes. G1 aberto, G2-a HOLD e G6 pendente.

**Complemento HIST-v3:** adicionados `routing_coverage.py` e `HIST3_ROUTING_COVERAGE.csv`; README, builder, testes e manifesto SHA256 atualizados. São **14 arquivos no módulo HIST-v3**; 36 testes locais novos, total CI previsto **349**. Cobertura por fonte: 100/484 domínios admitidos apenas sob hipóteses documentais, 384 lacunas. Sem validação no OpenHoldem real.

## Benchmark de piso R10d + 3bet HU v1 (DRAFT, não release)
- [benchmarks/r10d_floor/](benchmarks/r10d_floor/): 8 arquivos, incluindo inventário congelado (fonte Git blob/SHA), 14 capacidades, 12 testes, relatório determinístico, contrato de promoção explicitamente false e manifesto SHA.
- [portability/p3bet_hu_v1/](portability/p3bet_hu_v1/): 8 arquivos, incluindo `threebet_hu_postflop.oppl` (39 ações), captura de intenção RFI/VS_OPEN (9+44 tags), `preflop_srp_and_3bet_hu_draft.oppl` integrado, gerador, interpretador, 15 testes, documentação e manifesto SHA.
- 27 testes novos, 376 esperados em CI; todos os ranges preflop históricos e fontes anteriores mantidos. **Sem operação OpenHoldem real.** 14/14 famílias da meta R10d ainda não têm status VERIFIED. Não declarar release possível.

## SRP 3-way v1 — incremento DRAFT sobre p3bet_hu_v1
- [portability/p3way_srp_v1](portability/p3way_srp_v1/): 8 arquivos versionados (fonte 3way OpenPPL, source integrado, 33 marcações de intenção, gerador offline, intérprete restrito, 16 testes, README e manifesto SHA).
- [benchmarks/r10d_floor](benchmarks/r10d_floor/) atualizado na MESMA revisão: fonte ativa v1 3way, métricas 729 WHEN/90 Set/7 user_, M05 agora PARTIAL, relatório determinístico e SHA de benchmark regenerado.
- CI esperado 392 testes =349 históricos+15 3bet HU+12 benchmark+16 3way. Estado: DRAFT, sem comparação estratégica validada nem OpenHoldem real. **Piso R10d NOT MET**.

## ADR-031 — hotfix pós-flop DRAFT
Atualizados quatro ramos de nuts-call, testes, intérpretes, os dois integrados, READMEs, SHA e benchmark. 74 ações novas entre 3bet HU e SRP 3way (41+33), 733 WHEN integrados, 392 testes esperados. Nenhum release operacional, R10d piso NOT MET e sem execução OH.

## Multiway-v2 + LIMP-BB-v1 (20/11/2026, DRAFT)
- [multiway_v2/](portability/multiway_v2/) contém 9 arquivos versionados: políticas 4–6way e multiway→HU, integrado, gerador, intérprete, testes, matriz, README e SHA.
- [limped_bb_v1/](portability/limped_bb_v1/) contém 8 arquivos: política de BB limp, captura pré-flop, integrado ativo, gerador, intérprete, testes, README e SHA.
- [Benchmark R10d](benchmarks/r10d_floor/) repontado ao integrado atual e manifesto regenerado. 392 testes anteriores +25 +17 = **434** esperados. Os 14 gates finais não passaram; G6/execução real ainda bloqueado.

## MWT3, MLIMP2, P3BMW1 — módulos DRAFT não operacionais
- `portability/multiway_transitions_v3/`: 9 arquivos, 14 testes, 53 topologias de perdas intermediárias, 41 ações; `MWT3_SHA256SUMS.txt`.
- `portability/multilimp_bb_v2/`: 10 arquivos, 12 testes, 7 contextos BB-CHECK e 39 ações em potes de 2–5 limpers; `MLIMP2_SHA256SUMS.txt`.
- `portability/p3bet_multiway_v1/`: 9 arquivos, 12 testes, 43 ações e 117 topologias por street, com dois papéis PF; `P3BM1_SHA256SUMS.txt`.
- Fonte ativa: `portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl`. 521 testes no CI previstos, hashes gerados e preservação de todos os ranges anteriores. Sem replay real; R10d FLOOR NOT MET.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## ISO-1 (20/11/2026, DRAFT; NÃO release)
- Nova árvore: `portability/iso_raise_v1/` e integrado `iso_integrated_draft.oppl`, derivado do pai `portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl` sem alterar os 1.460 comandos `WHEN` ancestrais.
- Cinco contextos de isolamento pré-flop, 41 decisões pós-flop e 120 topologias. Teste, recomposição do integrado e SHA de integridade **aprovados na CI 44853164836** (534 execuções / 522 distintas por suíte); validação OpenHoldem permanece pendente. Fonte v0.6.1 intocada, **sem runtime OH**, sem promoção e sem prova de superação R10d. Ver [ADR-036](DECISIONS.md) e [HANDOFF](HANDOFF.md).

## BLISO-2 (20/11/2026) — novo integrado candidato, não release
- `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`, derivado de `portability/iso_raise_v1/iso_integrated_draft.oppl`, com todos os 1.666 `WHEN` ancestrais em ordem original. Mais 13 origens de preflop blind iso e 43 decisões postflop sobre 120 topologias. 18 testes novos de regressão aprovados no [workflow 44858080418](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418) (552 execuções / 540 deduplicados por suíte).
- Manifesto de conteúdo `BLISO2_SHA256SUMS.txt`, gerador e testes versionados. Nenhum chart RFI/VS_OPEN/VS_3BET alterado, sem confirmação de símbolos/ações no executável OH; release gate R10d segue bloqueado. Ver [ADR-037](DECISIONS.md).

## ISODEF-1 (21/11/2026) — candidato DRAFT, NÃO release
- Candidato: `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`, parent `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`. 87 novas linhas WHEN (10 preflop, 35 em helpers incluindo fallbacks e 42 ações pós-flop) para defesa após limp+isolation em dois nós. 2.007 WHEN integrados e 21 testes novos aprovados na [workflow 44860943038](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038) (573 execuções/561 deduplicadas).
- Proveniência fonte-first: `defense_handlists.oppl`, `defense_preflop_capture.oppl`, `defense_topology.oppl`, `defense_policy.oppl`, `build_defense.py`, `defense_interpreter.py`; manifestos SHA256 de módulo e benchmark separados. **Nenhum runtime OpenHoldem, nenhuma aprovação de pot odds, sizes, fallbacks ou métricas EV**. 14/14 gates R10d não VERIFIED. Ver ADR-038.

## OH-G1G6-1 (21/11/2026) — artefato de diagnóstico, NÃO versão de bot
- Pasta [portability/oh_runtime_gate_v1/](portability/oh_runtime_gate_v1/) com matriz de 10 casos, `evidence_gate.py`, 26 testes, hash collector PowerShell somente leitura, template `SYNTHETIC_BUNDLE.json`, `REVIEW_CHECKLIST.md` e `OHG1G6_SHA256SUMS.txt`. A política `portability/iso_defense_v1/iso_defense_integrated_draft.oppl` permanece **sem edição**.
- [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886) registrou 599 execuções, 587 deduplicadas por suíte, 30 suítes. Nenhum `runtime_approved=true`, nenhuma alteração de `PROMOTION_GATE.json`, nenhuma release operacional, G1 OPEN, G6 PENDING, G2-a HOLD e 0/14 R10d VERIFIED. Dados reais de replay NÃO incluídos.

## OH-SRC1 (21/11/2026) — auditoria de semântica fonte-first, NÃO release
- [portability/oh_source_audit_v1](portability/oh_source_audit_v1/README.md): `audit.py`, `SOURCE_FINDINGS.json`, 17 testes, README com referências a C++/manual, SHA256 e CI. [CI OH-SRC1](https://github.com/pmartins87/Heuristic6max/actions/runs/44864070437) aprovou 616 execuções / 604 deduplicadas em 31 suítes.
- Inventário da política ativa permanece **2.007 WHEN/159 f$/192 listas**, sem alterações na fórmula OpenPPL, nos ranges congelados, no ledger G2-a ou `PROMOTION_GATE.json`. Auditoria de 436 igualdades exatas de `PotSize` é alerta a tratar por domínio, não validação funcional R10d. Nenhum hash local necessário para construir. G1/G6 runtime, G2-a HOLD e 0/14 R10d VERIFIED permanecem.

## CI-LEAN1 — mudança de engenharia, não de versão do bot
Workflow `verify.yml` conserva as suítes únicas, SHA dos ancestrais, integrado e benchmark; evita reprocessar o mesmo R10d 6 vezes e reexecutar seus 12 testes duas vezes. PR draft não atesta qualidade; somente CI verde em PR pronta e nova CI verde em main. Nenhum `.oppl` ou `PROMOTION_GATE.json` alterado, G1/G6 de runtime pendentes, G2-a HOLD e 0/14 capacidades R10d VERIFIED.
