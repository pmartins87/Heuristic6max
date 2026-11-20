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
