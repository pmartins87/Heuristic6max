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
