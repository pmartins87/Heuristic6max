# Heuristic6max — fonte de verdade

Projeto de estratégia **heurística** de No-Limit Hold'em cash 6-max, inspirada em princípios GTO. **Não é solver nem bot operacional validado.**

**Estado (20/11/2026):** v0.5 — G0 aprovado; G1 aberto; G2 em auditoria/HOLD; G3–G7 pendentes. As tabelas RFI, VS_OPEN e VS_3BET são DRAFT. Nenhum desempenho/EV foi validado e os testes existentes são sintéticos.

## Leia nesta ordem ao continuar em outro chat/IA

1. [PROJECT_STATE.md](PROJECT_STATE.md) — versão e evidências atuais.
2. [ROADMAP.md](ROADMAP.md) — gates e critérios de aceitação.
3. [DECISIONS.md](DECISIONS.md) — decisões e justificativas.
4. [HANDOFF.md](HANDOFF.md) — como retomar e testar.
5. [CHANGELOG.md](CHANGELOG.md) — mudanças preservadas entre versões.
6. [data/](data/) — relatórios de auditoria disponíveis no repositório.

## Situação da v0.5

A v0.4 (114 testes) tinha 15 árvores VS_3BET, 169 classes cada, com 8 divergências agregadas acima de 8 pontos percentuais frente a benchmarks de condições não idênticas. A v0.5 mantém as decisões e adiciona a decomposição por mão; **119 testes passaram localmente**. A proporção de 4-bets de blefe na massa de 4-bets varia de 6,7% a 19,3% nos ranges atuais (não é meta GTO).

**Aviso de integridade:** se o código e os datasets completos da v0.5 ainda não estiverem presentes neste GitHub, o repositório é um checkpoint documental **incompleto**; consulte [PROJECT_STATE.md](PROJECT_STATE.md) antes de continuar. O ZIP local da v0.5 é o pacote integral para replicação e não deve ser reconstruído a partir apenas destes resumos.

**Regras de manutenção:** toda mudança relevante exige leitura e atualização destes arquivos; versões anteriores ficam preservadas; nenhum ajuste automático para igualar benchmarks de rake/árvore diferentes; `None` significa política ausente, nunca Fold/Check; não operar com dinheiro real antes de validação completa.
## Acompanhamento
- [Issue #1 — Sincronizar código e datasets da v0.5](https://github.com/pmartins87/Heuristic6max/issues/1) (bloqueador de portabilidade).
- [Issue #2 — Revisar 8 nós VS_3BET críticos](https://github.com/pmartins87/Heuristic6max/issues/2).
- Execute `python scripts/check_repository.py` para saber se o repositório contém a versão completa. Enquanto houver arquivos faltando, NÃO tratar o GitHub como réplica executável do pacote.

- [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md) registra hashes SHA-256 dos pacotes v0.1–v0.5 e o estado de sincronização.
