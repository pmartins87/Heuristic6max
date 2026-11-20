# Heuristic6max v0.6.1 — hotfix de integridade

Snapshot autocontido. Corrige a auditoria de preservação v0.6; **nenhuma decisão de poker foi alterada**. Fonte de verdade: README.md, PROJECT_STATE.md, DECISIONS.md, ROADMAP.md, HANDOFF.md, RELEASE_MANIFEST.md na raiz do GitHub.

Execução (Python 3.10+):

    python -m unittest -q
    python vs3_blocker_audit_v0_6.py

Espera-se 124 testes aprovados. Antes de executar o gerador, valide sha256sum -c SHA256SUMS.txt. A v0.6.1 preserva 50 arquivos ancestrais idênticos da v0.5 e regenera apenas o manifesto de integridade. Leia ERRATA_v0_6_1.md.

G1 aberto; G2-a HOLD; VS_4BET bloqueado.
