# Heuristic6max — fonte de verdade

Estratégia **heurística** de No-Limit Hold'em cash 6-max baseada em fundamentos de GTO, com contratos, ranges auditáveis e testes reprodutíveis. **Não é um solver; não é um bot operacional validado; não há comprovação de EV ou winrate.**

**Checkpoint ativo: v0.6.1 (20/11/2026)** — G0 aprovado; G1 aberto; G2-a em auditoria/HOLD; G3–G7 pendentes. RFI, VS_OPEN e VS_3BET continuam DRAFT.

## Retomada em novo chat ou IA
Leia, nesta ordem:
1. [PROJECT_STATE.md](PROJECT_STATE.md)
2. [ROADMAP.md](ROADMAP.md)
3. [DECISIONS.md](DECISIONS.md)
4. [HANDOFF.md](HANDOFF.md)
5. [CHANGELOG.md](CHANGELOG.md)
6. [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md)

## Código e dados completos no GitHub
- [v0.5 — 51 arquivos históricos preservados](gto6_heuristic_v0_5/)
- [v0.6 — 61 arquivos históricos, com errata de manifesto](gto6_heuristic_v0_6/)
- [v0.6.1 — 66 arquivos autocontidos; 124 testes; correção de integridade](gto6_heuristic_v0_6_1/)
- [Método e achados G2-a](gto6_heuristic_v0_6_1/G2A_METHOD_AND_FINDINGS_v0_6.md)
- [8 confrontos marcados para revisão](gto6_heuristic_v0_6_1/G2A_MAJOR_REVIEW_8_NODES_v0_6.csv)

Os **fontes e CSVs completos** agora estão commitados no repositório. Os arquivos ZIP são conveniências para transferência; não são necessários para reconstrução a partir do GitHub.

## Como verificar
    python scripts/check_repository.py
    cd gto6_heuristic_v0_6_1
    python -m unittest -q
    python vs3_blocker_audit_v0_6.py

**Regras permanentes:** alterar docs vivos após cada decisão; preservar versões; não igualar benchmarks incompatíveis artificialmente; política ausente deve retornar None, nunca Fold/Check silencioso; manter DeepCrusher/CrusherTBP intactos; não operar em mesas com dinheiro real até validação apropriada.

Issues: [#1 — importação concluída](https://github.com/pmartins87/Heuristic6max/issues/1) e [#2 — auditoria estratégica aberta](https://github.com/pmartins87/Heuristic6max/issues/2).

**Errata de rastreabilidade:** v0.6 marcou equivocadamente 51 arquivos ancestrais como SAME após regerar o manifesto. A v0.6.1 confirma **50/50 fontes de conteúdo idênticas** e 1 manifesto regenerado. Ver [ERRATA](gto6_heuristic_v0_6_1/ERRATA_v0_6_1.md).
