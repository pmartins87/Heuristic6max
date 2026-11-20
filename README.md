# Heuristic6max — fonte de verdade

Estratégia **heurística** de No-Limit Hold'em cash 6-max baseada em fundamentos de GTO, com contratos, ranges auditáveis e testes reprodutíveis. **Não é um solver; não é um bot operacional validado; não há comprovação de EV ou winrate.**

**Checkpoint ativo: auditoria v0.11 de fontes, sobre v0.10 (20/11/2026), sobre motor/ranges v0.6.1 preservados** — G0 aprovado; G1 aberto; G2-a em auditoria/HOLD; G3–G7 pendentes. RFI, VS_OPEN e VS_3BET continuam DRAFT.

## Auditoria v0.11 — charts públicas, sem substituir ranges
- [Método, fontes e critérios](audits/g2a_v0_11/README.md)
- [Fontes e premissas registradas](audits/g2a_v0_11/source_candidates.json)
- [Vereditos reproduzíveis](audits/g2a_v0_11/SOURCE_APPLICABILITY_v0_11.csv)
- Três fontes examinadas; **nenhuma apta à substituição direta** no cenário HJ abre 2,5 BB e CO 3-bet para 8 BB. Rake/cap alvo não documentados.
- **174 testes locais aprovados**, 11 novos na auditoria; nenhuma estratégia modificada.
- **Linguagem:** motor Python. OpenPPL/OpenHoldem permanece G6 pendente, sem código executável.
- **Critério de parada:** não prolongar toy-EV/EQR de parâmetros não calibrados sem nova evidência.

## Retomada em novo chat ou IA
Leia, nesta ordem:
1. [PROJECT_STATE.md](PROJECT_STATE.md)
2. [ROADMAP.md](ROADMAP.md)
3. [DECISIONS.md](DECISIONS.md)
4. [HANDOFF.md](HANDOFF.md)
5. [CHANGELOG.md](CHANGELOG.md)
6. [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md)


## Auditoria v0.10 — HJ/CO equities, sem mudança estratégica
- [Método e referência v0.10](audits/g2a_v0_10/README.md), [169 equities por classe](audits/g2a_v0_10/HJ_CO_EQUITY_169_REFERENCE_v0_10.csv), [15 conferências Monte Carlo](audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv).
- A fonte privada fornecida tinha 1.624.350 confrontos físicos ordenados, cobertura/reciprocidade conferidas; licença/autoria não documentadas, portanto **não publicar o bruto**. SHA-256 da fonte e método presentes no README da auditoria. Motor MC em Python stdlib pode reestimar sem a fonte original.
- Ex.: AQo 41,3101%, AJo 35,6951%, KJo 32,3099%, TT 44,0217% de **equidade bruta de showdown** contra a política 3bet do CO. Isso NÃO determina EV de call fora de posição, nem prova que folds existentes estão errados.
- 10 testes novos; total acumulado previsto **163 (124+7+11+11+10)**. Todos os ranges e o snapshot v0.6.1 permanecem intactos; G1 aberto, G2-a HOLD, G2-b bloqueado.

## Auditoria G2-a v0.9 — HJ vs CO, preços e contrafactuais (sem alterar ranges)
- [Método, limites e decisão](audits/g2a_v0_9/README.md)
- [169 classes com posterior e exposição à 3-bet](audits/g2a_v0_9/HJ_CO_169_CLASS_SCREEN_v0_9.csv)
- [15 classes candidatas: RFI vs resposta ao 3bet](audits/g2a_v0_9/HJ_CO_CANDIDATE_COUNTERFACTUALS_v0_9.csv)
- [36 fronteiras hipotéticas: rake/realização/sizing](audits/g2a_v0_9/HJ_CO_PRICE_FRONTIER_v0_9.csv)
- [Fonte e 11 testes incrementais](audits/g2a_v0_9/hj_co_frontier.py)

**153 testes previstos e verificáveis** (124+7+11+11). HJ/CO: FOLD 77,5377%, CALL 14,0392%, 4BET 8,4231%. Com abertura 2,5 e 3-bet para 8 BB, call adicional 5,5 BB / pote 17,5 BB = 31,43% de equidade imediata sem rake. Os cenários NÃO estimam equidade real, EV ou uma estratégia GTO; nenhum range foi alterado. G2-a HOLD.

## Auditoria G2-a v0.8 — defesa por mãos e interferência de terceiros (sem alterar ranges)
- [Método e resultados v0.8](audits/g2a_v0_8/README.md)
- [Mãos de maior contribuição aos folds](audits/g2a_v0_8/TOP_FOLD_CLASSES_8_v0_8.csv)
- [Famílias em 15 nós](audits/g2a_v0_8/DEFENSE_FAMILIES_15_v0_8.csv)
- [Sensibilidade a cold actions](audits/g2a_v0_8/COLD_ACTION_SENSITIVITY_15_v0_8.csv)
- [Código e 11 testes v0.8](audits/g2a_v0_8/defense_composition.py)

**142 testes locais** (124+7+11). Exemplo HJ-CO: **58,1119 pontos percentuais dos folds** vêm de quatro famílias (suited-outras, pares 22–66, broadways offsuit sem A e Ax offsuit). Isto NÃO significa que essas mãos deveriam dar call. Em BTN-SB, a pressão isolada anterior (+0,048 BB) desaparece sob pequena interferência hipotética do BB (~0,49%). Sem simulação de EV real; G2-a permanece HOLD.

## Auditoria G2-a v0.7 (sem alterar ranges)
- [Método e conclusões](audits/g2a_v0_7/README.md)
- [15 nós: fold contra preço da 3-bet](audits/g2a_v0_7/3BET_PRESSURE_ALL_15_v0_7.csv)
- [8 nós: detalhamento por mãos físicas do agressor](audits/g2a_v0_7/3BET_PRESSURE_HANDS_8_v0_7.csv)
- [Script e testes](audits/g2a_v0_7/pressure_audit.py)

7 dos 8 nós críticos exibem EV positivo para **blefe de equidade zero no experimento isolado**, sem cold actions e com Hero continuando = perda integral do investimento. **Não é EV real, não prova GTO nem autorização de alteração de estratégia.** O resultado altera a prioridade da revisão: investigar folds e defesas conjuntas (call + 4bet), não somente percentual de 4bet.

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


## PORT-0: novas regras devem ser portáveis na origem (ADR-016)
- [Contrato de portabilidade](PORTABILITY_CONTRACT.md): usar regras nativas OpenPPL ou uma representação declarativa que gere OpenPPL e simulação Python a partir da mesma fonte. Python de auditorias e testes permanece livre.
- [Piloto com 2 regras OpenPPL](portability/portable_rfi_probe.oppl), [intérprete Python](portability/oppl_probe.py) e [7 testes](portability/test_oppl_probe.py) em 3.042 estados. Não operacional e ainda sem testes no OpenHoldem real.
- Bloqueados até paridade demonstrada: mistura SHA256/Random, predicado source_quality=HIGH, None versus fallback automático e ajustes de RaiseTo ilegal.
- Versões e ranges anteriores permanecem preservados; G6 continua uma etapa futura.
