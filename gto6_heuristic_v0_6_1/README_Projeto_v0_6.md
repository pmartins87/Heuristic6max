# Heuristic6max v0.6 — checkpoint reprodutível de auditoria

O repositório GitHub `pmartins87/Heuristic6max` é a fonte de verdade. Esta pasta contém o snapshot v0.5 (51 arquivos) inalterado e o avanço G2-a da v0.6. **Não é um bot operacional, não foi validado em mesas, e não equivale à GTO.**

## Comandos (Python >= 3.10, biblioteca padrão)

```bash
cd gto6_heuristic_v0_6
python -m unittest -q
python vs3_blocker_audit_v0_6.py
```

A saída dos testes deve ter 124 testes `OK`; o segundo comando regenera os três CSVs G2A, sem mudar decisões. Compare SHA256SUMS.txt com `sha256sum -c SHA256SUMS.txt` antes de regenerar.

## Documentação obrigatória
Leia os documentos vivos na **raiz do repositório**: `README.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md`, `CHANGELOG.md`, `RELEASE_MANIFEST.md`. Leia também `G2A_METHOD_AND_FINDINGS_v0_6.md` nesta pasta.

## Stop rules
Não alterar as tabelas RFI, VS_OPEN ou VS_3BET para atingir percentuais de benchmarks com premissas distintas; não iniciar VS_4BET sem decisão no gate G2-a; replays reais do OpenHoldem são pré-requisito de G1; políticas ausentes retornam None e nunca fold silencioso.
