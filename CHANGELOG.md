# Histórico consolidado — Heuristic6max

- **v0.1:** arquitetura inicial, 22 testes.
- **v0.2:** reconstrutor sintético + RFI 5 × 169, 71 testes.
- **v0.3:** VS_OPEN 15 × 169, 91 testes.
- **v0.4:** VS_3BET 15 × 169, 114 testes; 8 divergências maiores frente a benchmark não comparável.
- **v0.5:** decomposição por mão sem mudar as ações v0.4; 119 testes; 51 arquivos, agora totalmente importados no GitHub.
- **v0.6 (20/11/2026):** correção *de medição* de VS_3BET com card removal e modelo de 3-bet VS_OPEN. 15 nós, 1.326 combos físicos, 124 testes, 61 arquivos no snapshot completo. Mudança de frequências auditadas: -0,409 a -1,766 p.p. em 4bet condicional. **Nenhuma ação estratégica foi alterada; G2-a permanece HOLD.**

Consulte [DECISIONS.md](DECISIONS.md) para justificativas e [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md) para hashes e commits. Não confunda teste de infraestrutura com validação GTO.
