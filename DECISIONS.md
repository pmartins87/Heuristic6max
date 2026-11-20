# Registro de decisões técnicas — Heuristic6max

**ADR-001 — Heurística, não solver (MANTIDA).** Construir cash 6-max com heurísticas GTO auditáveis, sem alegar GTO exata, EV ótimo nem lucratividade.

**ADR-002 — GitHub fonte de verdade (MANTIDA).** Ler e atualizar README.md, PROJECT_STATE.md, ROADMAP.md, DECISIONS.md, CHANGELOG.md, HANDOFF.md, RELEASE_MANIFEST.md em cada checkpoint. Preservar snapshots anteriores.

**ADR-003 — Não alterar v0.4 por benchmarks incompatíveis (MANTIDA).** Rake/árvore diferentes inviabilizam otimização por simples matching. Não usar diferenças agregadas para justificar mudanças estratégicas.

**ADR-004 — Ausência explícita (MANTIDA).** Política ausente = None, nunca Fold/Check automático.

**ADR-005 — Escada de evidência (MANTIDA).** (1) testes estáticos/sintéticos; (2) replay real; (3) benchmark/EV comparável; (4) integração OpenHoldem; nenhum nível superior é inferido pelo inferior.

**ADR-006 — Separação do DeepCrusher/CrusherTBP (MANTIDA).** Não importar decisões antigas sem validar a economia/árvore.

**ADR-007 — Sincronização de fontes (20/11/2026).** Publicar snapshots v0.5 (51 fontes) e v0.6 (61 fontes) completos no GitHub, sem depender de ZIP externo. Verificar testes, arquivo de hashes e presença de conteúdo. Substitui o bloqueio documental da Issue #1.

**ADR-008 — Corrigir contabilidade antes de mudar strategy (20/11/2026).** Implementada em v0.6 uma auditoria de P(ação | RFI, 3bet) com 1.326 combinações, o modelo VS_OPEN do vilão e card removal. Não se altera a política; compara-se antes/depois e se mantém HOLD. Justificativa: o benchmark anterior usava massa condicional somente ao RFI, sem atualizar pela ocorrência da 3bet.

**ADR-009 — Critério estratégico (20/11/2026).** Manter G2-a aberto; não iniciar VS_4BET sem avaliar os oito confrontos sob rake, sizings e ranges de vilão coerentes. Só mudar recomendação perante evidência nova ou erro comprovado.

**ADR-010 — Errata da comparação de snapshots (20/11/2026).** A v0.6 mediu 51/51 SAME antes da regeneração do SHA256SUMS.txt, produzindo um relatório de preservação incorreto e falha do primeiro CI. NÃO alterar a v0.6 já publicada: preservar como checkpoint histórico, adicionar v0.6.1 com 50/50 arquivos-base de conteúdo idênticos e 1/1 manifesto regenerado. O verificador deve validar cada manifesto por seus próprios hashes. 124 testes sintéticos inalterados. **Válido.**

**ADR-011 — Nova métrica de vulnerabilidade condicional (20/11/2026).** A auditoria v0.7 testa matematicamente o preço de uma 3bet de vilão por combinação física, com card removal, assumindo isolamento da disputa e equidade zero do agressor caso o Hero continue. 7/8 nós críticos indicam pressão positiva, mas isto não prova lucro real nem requer alteração automática. Prioridade muda da mera comparação de 4bet com benchmarks incompatíveis para **fold + call + 4bet versus sizing**. Manter HOLD G2-a, ranges v0.6.1 imutáveis e G2-b bloqueado. [Método e ressalvas](audits/g2a_v0_7/README.md). **Válido.**
