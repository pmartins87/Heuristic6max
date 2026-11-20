# Heuristic6max — fonte de verdade

## VS_3BET-MVP — árvore pré-flop em OpenPPL (20/11/2026; DRAFT)
- [Código, testes e contrato de integração](portability/vs_3bet_mvp/README.md); [mapeamento 15 × 169](portability/vs_3bet_mvp/VS3_2535_MAPPING.csv).
- **888 decisões alcançáveis** de 2.535 classes/confrontos, 1.647 impossíveis após RFI (nenhuma ação inventada). **90 handlists + 135 regras**, 23 testes novos; baseline RFI/VS_OPEN/VS_3BET v0.6.1 **intacta**.
- [Fonte OpenPPL VS_3BET](portability/vs_3bet_mvp/vs_3bet_6max_mvp.oppl) e [fonte única pré-flop RFI+VS_OPEN+VS_3BET](portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl): **277 regras** com um só `f$preflop`. Cobrem apenas sizings/árvores 100BB previstos, **não** são bot operacional.
- Escolhas técnicas: `Raises=1` (contagem só dos adversários), `BotRaisedBeforeFlop`, `RaisesSinceLastPlay=1`, posições de primeiro/último raiser e stack no início da rodada. Sem replay real OH nem fallback controlado: G1 aberto, G2-a HOLD, G6 pendente.
- **Foco prático:** bot heurístico aproximadamente GTO, sem solver próprio ou prova científica de EV. Regressões servem para não quebrar transcrição e histórico.

## VS_OPEN-MVP: 15 árvores pré-flop em OpenPPL (DRAFT — NÃO operacional)
- [Código, regra de escopo e 19 testes](portability/vs_open_mvp/README.md), [fonte VS_OPEN das 2.535 decisões](portability/vs_open_mvp/vs_open_6max_mvp.oppl) e [pré-flop combinado RFI + VS_OPEN](portability/vs_open_mvp/preflop_rfi_vsopen_draft.oppl).
- **15 confrontos × 169 classes = 2.535 estados**, 81 listas disjuntas por confronto, 121 regras OpenPPL de VS_OPEN; combinadas com 21 regras RFI anteriores = **142 regras na mesma função preflop** e 3.380 estados de classe/par ou classe/posição.
- Ações 3BET/CALL/FOLD e todos os mixes `randomhand` copiados sem alterações da v0.6.1; guardas `Raises=1`, `Calls=0`, `FirstRaiserPosition` e `LastRaiserPosition` + tamanho de open, call e stack. 3bet RaiseTo 8, 10.25 ou 9.6 BB.
- **19 testes incrementais**; **273 testes acumulados esperados na CI**. Sem replay em OpenHoldem ou fallback seguro; G2-a HOLD em estratégia, G6 pendente. Próximo módulo: VS_3BET sobre snapshot intacto.

## RFI-MVP 6-max — módulo OpenPPL das cinco posições (20/11/2026)
- **[Fonte OpenPPL e documentação](portability/rfi_mvp/README.md)** · [845 linhas por mão/posição](portability/rfi_mvp/RFI_6MAX_845_MAPPING.csv).
- Implementadas 5 posições LJ/HJ/CO/BTN/SB, **845 classes de situação**, 21 regras e os cinco mixes por `randomhand`; SB preserva ramo de limp (`Call`), não apenas raise/fold.
- Fonte estratégica OpenPPL única; Python offline apenas gera/verifica. Frequências e decisões da **v0.6.1 são integralmente preservadas**.
- **12 testes novos** (254 acumulados esperados no CI), sem novas pesquisas de EV imaginário. **Não é bot operacional completo**: VS_OPEN/VS_3BET, fallback e pós-flop pendem; OpenHoldem real não foi executado.
- **Prioridade de engenharia:** converter VS_OPEN a partir das tabelas existentes, mantendo gate de integração OH separado do desenvolvimento da heurística.

## PORT-3 / RPL-0 — auditor de evidência OpenHoldem (sem aprovação de runtime)
- [Método, provas e instruções offline](portability/port3/README.md), [auditor Python](portability/port3/replay_audit.py), [27 testes](portability/port3/test_replay_audit.py).
- O auditor lê o **mesmo arquivo OpenPPL PORT-2**, exige `randomhand` observado, símbolo/estado do replay, SHA da fórmula, **ação da fórmula** e **ação final**. Recusa no-match como fail-closed e detecta fallback/sizing divergente.
- **Nenhuma captura OH real foi produzida**. CSV sintético contém **5 `STATIC_ONLY` e 1 `BLOCKED_NO_MATCH`**; não há `PASS` operacional automático, mesmo com arquivo de evidência. A versão de OH, logs e observações reais seguem pendentes.
- 27 testes incrementais; **242 testes esperados em CI** = 215 anteriores + 27. Preservados todos os ranges/snapshots v0.6.1; G1 aberto, G2-a HOLD, G6 pendente.

## PORT-2: mix nativo OpenPPL com `randomhand` (estático, NÃO operacional)
- [Fonte única OpenPPL, interpretador e 19 testes](portability/port2/README.md); [mapeamento das 169 classes LJ](portability/port2/PORT2_LJ_169_MAPPING.csv).
- KJo: raise 40% quando `randomhand < 0.40` e fold 60% caso contrário; 43 classes com raise puro, 125 com fold puro, **nenhuma mudança na baseline v0.6.1**.
- 19 testes incrementais; total de **215 testes esperados no CI** (196 anteriores + 19). São testes de fonte estática, **não testam o OpenHoldem real**.
- PORT-2 **parcial**, sem promoção operacional: estabilidade/valor do símbolo no OH instalado, fallback, scraping e sizing final seguem exigindo replay em ambiente sem apostas.

Estratégia **heurística** de No-Limit Hold'em cash 6-max baseada em fundamentos de GTO, com contratos, ranges auditáveis e testes reprodutíveis. **Não é um solver; não é um bot operacional validado; não há comprovação de EV ou winrate.**

**Checkpoint ativo: RFI-MVP OpenPPL 5 posições (20/11/2026), sobre PORT-3 e estratégia v0.6.1 preservada** — G0 aprovado; G1 aberto; G2-a em auditoria/HOLD; G3–G7 pendentes. RFI, VS_OPEN e VS_3BET continuam DRAFT.

## PORT-1 parcial — RFI LJ (20/11/2026)

- [Código OpenPPL, testes e fonte única](portability/port1/README.md), [cobertura das 169 classes](portability/port1/PORT1_LJ_169_MAPPING.csv).
- 43 RAISE puros e 125 FOLD puros representados em duas listas/regras OpenPPL; **KJo (40% raise/60% fold) permanece NÃO MAPEADO** para não quebrar a estratégia mista.
- 15 testes incrementais em Python interpretam as regras OpenPPL diretamente, sem estratégia paralela. Contagem total esperada 174+7+15 = **196 testes**.
- **PORT-1 permanece ABERTO**, pois símbolos, sorteio estável, ação ilegal e fallback ainda precisam de teste no OpenHoldem real. Nenhum range estratégico mudou.

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
