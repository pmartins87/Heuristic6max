# Handoff — retomar em outro chat, computador ou IA

## Regra principal
**Leia sempre** README.md → PROJECT_STATE.md → ROADMAP.md → DECISIONS.md → CHANGELOG.md → RELEASE_MANIFEST.md → este HANDOFF.md. Compare-os com os arquivos GitHub e commits reais antes de modificar. O repositório é a fonte de verdade; mensagens antigas podem estar obsoletas.

## Retomada reproduzível
Clonar https://github.com/pmartins87/Heuristic6max e executar:

    python scripts/check_repository.py
    cd gto6_heuristic_v0_6_1
    sha256sum -c SHA256SUMS.txt
    python -m unittest -q
    python vs3_blocker_audit_v0_6.py

Esperado: 124 testes OK. São testes **sintéticos**, não validação OpenHoldem, GTO nem EV. Para Windows, usar um verificador SHA256 equivalente em vez de sha256sum, se indisponível.

## Auditoria incremental v0.7

    python -m unittest discover -s audits/g2a_v0_7 -p 'test_*.py' -q
    python audits/g2a_v0_7/pressure_audit.py

7 testes novos somados aos 124 de v0.6.1. Relatórios e limitações: [audits/g2a_v0_7/README.md](audits/g2a_v0_7/README.md). O script de auditoria **não altera políticas**. GitHub Actions roda ambos e confirma que os CSVs produzidos coincidem com os versionados.

## Localização
- Histórico integral imutável: gto6_heuristic_v0_5/ (51 arquivos).
- v0.6 histórica: gto6_heuristic_v0_6/ (61 arquivos; vide errata).
- Snapshot mais recente **v0.6.1**: gto6_heuristic_v0_6_1/ (66 arquivos).
- Método/cálculo: gto6_heuristic_v0_6_1/G2A_METHOD_AND_FINDINGS_v0_6.md.
- Relatórios: G2A_VS3_BLOCKER_15_NODES_v0_6.csv, G2A_VS3_BLOCKER_TOP_HANDS_v0_6.csv e G2A_MAJOR_REVIEW_8_NODES_v0_6.csv.
- Inventário de preservação: V05_PRESERVATION_AUDIT_v0_6_1.csv (50/50 SAME; SHA256SUMS.txt REGENERATED_EXPECTED).

## Estado exato
G0 aprovado; G1 aberto (falta replay real); G2-a HOLD (nova auditoria de pressão v0.7 concluída, revisão estratégica dos oito nós ainda incompleta); G2-b VS_4BET bloqueado; G3–G7 pendentes. Nenhum range RFI/VS_OPEN/VS_3BET foi alterado desde v0.4. Não modificar DeepCrusher/CrusherTBP.

## Próximo passo
Revisar por classe os oito MAJOR_REVIEW com comparações rake/sizings equivalentes, ou registrar lacunas. Só modificar política com evidência, testes de regressão, justificativa, changelog e atualização documental. Não usar em mesas com dinheiro real.

**Correção obrigatória de continuidade:** leia [ERRATA v0.6.1](gto6_heuristic_v0_6_1/ERRATA_v0_6_1.md). O primeiro CI falhou por comparar manifestos diferentes como se devessem ser byte-idênticos; a v0.6.1 corrigiu somente metadados.

**Primeira ação ao retomar:** conferir GitHub Actions mais recente, ler ADR-011 e verificar que `audits/g2a_v0_7/` ainda referencia v0.6.1. A próxima mudança estratégica exige premissas compatíveis de rake, sizing e adversários atrás.

## Auditoria incremental v0.8 — última etapa antes de editar ranges

    python -m unittest discover -s audits/g2a_v0_8 -p 'test_*.py' -q
    python audits/g2a_v0_8/defense_composition.py
    cd audits/g2a_v0_8 && sha256sum -c AUDIT_SHA256SUMS.txt

A auditoria v0.8 agrega 11 testes aos 131 da v0.7/base: **142 testes locais**. Fonte: [README v0.8](audits/g2a_v0_8/README.md). O CI confere determinismo dos quatro CSVs versionados. **Não usar o ranking de folds como recomendação de call.** Nenhuma política foi alterada; próxima etapa é análise EV por mão/rake/sizing e replays de teste. Lembre-se de rever os sete documentos vivos antes de qualquer nova implementação.

**Atenção CI:** v0.8 passou por um ajuste de desempate estável (Python 3.11/3.13). Execute os testes + regeneração dos quatro CSVs + `git diff` + `sha256sum -c AUDIT_SHA256SUMS.txt`. Não comparar ordenação de floats sem chave estável.

## Auditoria incremental v0.9 — HJ–CO

    python -m unittest discover -s audits/g2a_v0_9 -p 'test_*.py' -q
    python audits/g2a_v0_9/hj_co_frontier.py
    cd audits/g2a_v0_9 && sha256sum -c AUDIT_SHA256SUMS.txt

- [Método e relatórios HJ–CO](audits/g2a_v0_9/README.md): 169 classes, 15 candidatas, 36 cenários artificiais de preço, 11 testes novos; total esperado 153.
- Baseline de estratégia v0.6.1 preservada. P(HJ fold | RFI, CO 3bet)=77,53771778%, call=14,03919921%, 4bet=8,42308301%.
- Poda de RFI e deslocamento de FOLD->CALL/4BET são **contrafactuais** sem EV conhecido e NÃO autorizam mudança; rake 5/8% e realização 60–100% são apenas hipóteses.
- GitHub é atualizado diretamente neste projeto; **não solicitar upload manual ao usuário**. Ler estado e verificar CI antes de continuar. G2-a ainda HOLD; G2-b bloqueado.

## Retomada v0.10 — equity HJ vs CO
Primeiro leia [auditoria v0.10](audits/g2a_v0_10/README.md) e [ADR-014](DECISIONS.md). Para validar o novo trabalho, desde a raiz do checkout:

    python -m unittest discover -s audits/g2a_v0_10 -p 'test_*.py' -q
    python audits/g2a_v0_10/equity_audit.py --mc --samples 50000 --output audits/g2a_v0_10/HJ_CO_EQUITY_15_MONTE_CARLO_v0_10.csv
    cd audits/g2a_v0_10 && sha256sum -c AUDIT_SHA256SUMS.txt

Dados 169 classes derivados de PreFlopEquities.zip privado (SHA no README, origem/licença não certificadas); ZIP bruto propositalmente ausente no GitHub. Para reproduzir os valores exatos da referência, recuperar cópia autorizada com hash idêntico; para reestimar a partir apenas do GitHub, usar Monte Carlo stdlib. São 10 testes adicionais (163 total esperado); não operar bot nem editar ranges. Próximo passo: EV de call/4bet, realização e rake reais ou cenários com incerteza, antes de qualquer decisão. **A integração GitHub permite atualizações diretas, sem upload manual do usuário.**

## Auditoria incremental v0.11 — charts e status de OpenPPL

    python -m unittest discover -s audits/g2a_v0_11 -p 'test_*.py' -q
    python audits/g2a_v0_11/source_gate.py
    cd audits/g2a_v0_11 && sha256sum -c AUDIT_SHA256SUMS.txt

- [Método e registro de fontes](audits/g2a_v0_11/README.md): 11 testes, **174 totais**; três fontes classificadas REFERENCE_ONLY. Não importar arquivos licenciados nem frequências incompatíveis.
- **Estado da linguagem:** motor e estratégia em Python. Nenhum OpenPPL operacional no repositório; etapa G6 ainda não iniciada.
- **Critério de parada:** não ampliar indefinidamente os cenários hipotéticos HJ/CO sem rake, cap, sizing, fonte comparável ou replay real. Próximo gate orientado por evidência G1/G2-a.
- Usuário não precisa enviar arquivos ao GitHub: manter integração direta, docs vivos e CI verificada.


## PORT-0 obrigatório antes de novos módulos de estratégia (ADR-016)
Leia [PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md). Cada decisão exportável deve ser escrita como OpenPPL nativa ou representação estrita geradora das duas camadas. Python de testes interpreta as MESMAS regras, nunca uma versão estratégica reinventada. Comandos de prova:
- python -m unittest discover -s portability -p 'test_*.py' -q
- python portability/oppl_probe.py
São 7 testes novos e 3.042 estados simulados; OpenHoldem NÃO validado. No-match, raise ilegal, source_quality HIGH e mixed com SHA256 continuam não mapeados. G1/G2/G6 preservados. Não solicitar upload manual ao usuário.

## PORT-1 parcial — fonte OpenPPL LJ RFI

Na raiz do repositório, execute:

    python -m unittest discover -s portability/port1 -p 'test_*.py' -q
    python portability/port1/generate_port1.py
    git diff --exit-code -- portability/port1/lj_rfi_pure_port1.oppl portability/port1/PORT1_LJ_169_MAPPING.csv
    cd portability/port1 && sha256sum -c PORT1_SHA256SUMS.txt

- 15 testes novos; total esperado 196 (174 auditorias +7 PORT-0 +15 PORT-1).
- 168/169 classes LJ com ações puras, KJo 40% RFI não mapeado, sem fail-closed assegurado no OH.
- Ler [PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md) e [README PORT-1](portability/port1/README.md) antes de modificar qualquer lógica. Nem OpenPPL nem interpretador são bot operacional; portar só após validação em OH.
- Nunca pedir upload manual: o GitHub deve ser atualizado pela conexão. Consultar G1/G2-a/HOLD e preservar os sete documentos vivos.

## PORT-2 — mix nativo `randomhand`, checkpoint 20/11/2026
- Ler primeiro [portability/port2/README.md](portability/port2/README.md) e [PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md); PORT-1 foi preservado como histórico, mas a lacuna KJo 40/60 de expressabilidade estática está coberta.
- Rodar da raiz: `python -m unittest discover -s portability/port2 -p 'test_*.py' -q`, depois `python portability/port2/generate_port2.py`; verificar `git diff --exit-code -- portability/port2/*.oppl portability/port2/*.csv` e `(cd portability/port2 && sha256sum -c PORT2_SHA256SUMS.txt)`.
- 19 novos testes, 215 no total previsto. Não executar o .oppl em dinheiro real; no-match em Python não equivale a falha segura de OpenHoldem. **Próximo gate:** replay real de teste, observação de `randomhand`, action final/size e fallback. Somente passar a outro nó misto após resolver correlação e mecanismos por nó.

## PORT-3 / replay evidence (20/11/2026) — ler ANTES de promover OPPL
- [Contrato e passos para replay offline](portability/port3/README.md), [auditor](portability/port3/replay_audit.py), [fixtures estritamente sintéticas](portability/port3/SYNTHETIC_REPLAY_INPUT.csv). O código NÃO invoca OpenHoldem nem fornece ação ao cliente.
- Testar: `python -m unittest discover -s portability/port3 -p 'test_*.py' -q`; `python portability/port3/replay_audit.py`; `git diff --exit-code -- portability/port3/SYNTHETIC_REPLAY_REPORT.csv`; `cd portability/port3 && sha256sum -c PORT3_SHA256SUMS.txt`.
- **Esperado:** 27 testes e 5 STATIC_ONLY + 1 BLOCKED_NO_MATCH; 242 testes totais previstos. `READY_FOR_MANUAL_REVIEW` não prova autenticidade, parsing por OH nem segurança. O runtime OH permanece **sem teste**.
- Evidências reais futuras DEVEM ser capturadas em OHReplay/ManualMode offline e mantidas fora do GitHub público. Confrontar `Best action` com `Action taken` e verificar guardas/randomhand antes de liberar gate. Não reabrir discussão da mistura KJo sem nova falha concreta; não mexer nos 3 ranges.

## Checkpoint RFI-MVP 6-max (20/11/2026) — próximo trabalho estratégico
- [Fonte OpenPPL e regras RFI-MVP](portability/rfi_mvp/README.md); `rfi_6max_mvp.oppl` cobre 845 cenários first-in, sem repetir estratégia no Python.
- Para checar: `python -m unittest discover -s portability/rfi_mvp -p 'test_*.py' -q`; `python portability/rfi_mvp/generate_rfi_mvp.py`; `git diff --exit-code -- portability/rfi_mvp/rfi_6max_mvp.oppl portability/rfi_mvp/RFI_6MAX_845_MAPPING.csv`; `cd portability/rfi_mvp && sha256sum -c RFI_MVP_SHA256SUMS.txt`.
- 12 novos testes (254 acumulados esperados); cinco mixes sem aproximações puras, SB com limp. Não recodificar um segundo runtime Python, não operar em apostas, não tratar no-match como None operacional.
- **Próximo passo:** VS_OPEN na mesma linguagem e estratégia imutável. Não continuar criando auditorias econômicas teóricas sem relação com avanço concreto. Versão OH e replay real ainda pendentes, guardados para o gate de integração.

## VS_OPEN-MVP (20/11/2026) — próximo passo VS_3BET sem pivot
- Fonte e limitações: [portability/vs_open_mvp/README.md](portability/vs_open_mvp/README.md), **`vs_open_6max_mvp.oppl`** (15×169) e **`preflop_rfi_vsopen_draft.oppl`** (unificação de RFI 845 + VS_OPEN 2535; 142 regras).
- Executar da raiz: `python -m unittest discover -s portability/vs_open_mvp -p 'test_*.py' -q`; `python portability/vs_open_mvp/generate_vs_open_mvp.py`; `git diff --exit-code -- portability/vs_open_mvp/*.oppl portability/vs_open_mvp/VS_OPEN_2535_MAPPING.csv`; `(cd portability/vs_open_mvp && sha256sum -c VS_OPEN_MVP_SHA256SUMS.txt)`.
- **19 testes novos, 273 acumulados esperados**, SHA256 verifica 7 arquivos. Nenhum arquivo histórico de estratégia alterado. FirstRaiserPosition/LastRaiserPosition dependem do OH real; no-match não garante fallback. Nunca chamar o combinado de bot pronto.
- Próximo: portar **VS_3BET v0.6.1** ao mesmo `##f$preflop##`, usando o arquivo existente como fonte de verdade. Manter 7 docs vivos e issue #2/#3. Não iniciar G2-b/VS_4BET; G2-a permanece HOLD para alterações estratégicas. Testes de replay OH offline continuam pendentes.

## VS_3BET-MVP — retomar daqui (20/11/2026)
- Fontes atuais de estratégia v0.6.1 continuam **sem qualquer alteração**. [Novo módulo](portability/vs_3bet_mvp/README.md), [OpenPPL VS_3BET](portability/vs_3bet_mvp/vs_3bet_6max_mvp.oppl), [OpenPPL integrado 277 regras](portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl).
- Da raiz: `python -m unittest discover -s portability/vs_3bet_mvp -p 'test_*.py' -q`; `python portability/vs_3bet_mvp/generate_vs3_mvp.py`; `git diff --exit-code -- portability/vs_3bet_mvp/*.oppl portability/vs_3bet_mvp/*.csv`; `(cd portability/vs_3bet_mvp && sha256sum -c VS3_MVP_SHA256SUMS.txt)`.
- **23 testes novos, 277 acumulados esperados; 888 entradas viáveis, 1.647 explicitamente sem regra**, 135 novas regras em VS3, 277 combinadas. O OPPL combinado **não foi executado** em OpenHoldem. Seu uso depende de verificar histórico, stacks e fallback no OH real.
- Próximo passo pragmático: replay offline de VS_3BET para confirmar `BotRaisedBeforeFlop`, `RaisesSinceLastPlay`, `First/LastRaiserPosition`, `StackSizeAtBeginningOfCurrentRound`, sizing real e ação final; depois G3 pós-flop SRP HU. Não iniciar G2-b/VS_4BET antes de critério anterior, não duplicar árvores Python em runtime.

## G3 prático SRP HU — checkpoint 20/11/2026
- **Primeiro ler** [portability/srp_hu_mvp/README.md](portability/srp_hu_mvp/README.md) e depois [PORTABILITY_CONTRACT.md](PORTABILITY_CONTRACT.md) antes de editar pós-flop.
- Artefatos: `srp_hu_postflop_draft.oppl` (33 regras + 5 helpers); `preflop_and_srp_hu_draft.oppl` (integração direta com preflop VS3); `srp_source_interpreter.py` (teste de interpretação da MESMA fonte), 18 testes e hashes.
- Executar da raiz: `python -m unittest discover -s portability/srp_hu_mvp -p 'test_*.py' -q`; `python portability/srp_hu_mvp/rebuild_combined.py`; `git diff --exit-code -- portability/srp_hu_mvp/preflop_and_srp_hu_draft.oppl`; `cd portability/srp_hu_mvp && sha256sum -c SRP_HU_SHA256SUMS.txt`.
- **Não autorizar bot para mesa com dinheiro**: ainda sem OH real, sem bloqueio garantido de no-match e sem prova de identificação inequívoca do pote SRP no caso de limpers/isolamento. Falha na documentação/CI é gate técnico, mas não transformar MVP de bot heurístico em pesquisa científica.
- Próximo passo: validar parser e ação final com OHReplay/ManualMode offline, resolver a ambiguidade de limpers e evoluir regras pós-flop por textura, mantendo ranges G2-a HOLD.

## Retomada obrigatória G3-HIST-v1 — 20/11/2026
- Consulte primeiro [STRATEGY_ARCHITECTURE.md](STRATEGY_ARCHITECTURE.md) e [portability/srp_history_v1/README.md](portability/srp_history_v1/README.md). O bot precisa ser COMPLETO e sensível ao histórico, com grafos de decisões escaláveis; código DRAFT, não certificado como GTO exato.
- Rodar `python portability/srp_history_v1/build_history.py`; `python -m unittest discover -s portability/srp_history_v1 -p 'test_*.py' -q`; `git diff --exit-code -- portability/srp_history_v1/srp_hu_history_v1.oppl portability/srp_history_v1/preflop_srp_history_v1.oppl portability/srp_history_v1/HISTORY_FLOP_TURN_9_PATHS.csv`; `(cd portability/srp_history_v1 && sha256sum -c HISTORY_SHA256SUMS.txt)`.
- 18 testes novos (295 totais previstos), 58 regras SRP HU pós-flop, 9 trajetórias e 24 funções. Os 277 ramos pré-flop, v0.6.1 e SRP-HU G3 anteriores permanecem imutáveis; nova fonte OpenPPL em `portability/srp_history_v1/history_overlay.oppl`.
- **Cuidado crítico:** no-match do Python não é fallback seguro no OH; símbolos de histórico por órbita podem falhar sob scrape não estável. Histórico 'limper+iso' ainda pode contaminar classificação SRP. **Próxima etapa** aumentar cobertura de raise/check-raise e histórico verdadeiro antes de escalar pelo número bruto de regras. Não iniciar apostas reais.

## G3-HIST-v2 — retomada do bot completo (20/11/2026)
- **Leia:** [STRATEGY_ARCHITECTURE.md](STRATEGY_ARCHITECTURE.md) e [portability/srp_history_v2/README.md](portability/srp_history_v2/README.md) **antes** de alterar árvores. HIST-v1 continua histórico imutável.
- Reproduzir: `python portability/srp_history_v2/build_history_v2.py`; `python -m unittest discover -s portability/srp_history_v2 -p 'test_*.py' -q`; `git diff --exit-code -- portability/srp_history_v2/srp_hu_history_v2.oppl portability/srp_history_v2/preflop_srp_history_v2.oppl portability/srp_history_v2/HISTORY_FLOP_TURN_36_PATHS.csv`; `(cd portability/srp_history_v2 && sha256sum -c HISTORY_V2_SHA256SUMS.txt)`.
- **18 novos testes, 313 totais esperados**, 36 históricos, 75 regras de ação e 70 funções. Quatro fontes preservadas: v0.6.1, pré-flop combinado, SRP G3, HIST-v1. R/H/M são inferências de flags, não prova cronológica real; no-match do Python é inseguro como fallback OH.
- Próxima prioridade: reconciliar sequência ordenada e condições de pote antes de multiplicar por board/sizing; depois expandir linha completa e pós-flop 3bet/multiway. NÃO anunciar bot operacional, sem replays executáveis.

## HIST-v3 — histórico cronológico e correção da semântica de call (20/11/2026)
- Começar por [portability/srp_history_v3/README.md](portability/srp_history_v3/README.md), [HIST3_484_CHRONOLOGICAL_PATHS.csv](portability/srp_history_v3/HIST3_484_CHRONOLOGICAL_PATHS.csv), [HIST3_OBSERVABILITY.csv](portability/srp_history_v3/HIST3_OBSERVABILITY.csv). A HIST-v2 era 6×6 combinações agregadas; novos 484 são apenas cenários legais de sequência, **não 484 respostas estratégicas prontas**.
- Rodar: `python -m unittest discover -s portability/srp_history_v3 -p 'test_*.py' -q`; `python portability/srp_history_v3/build_history_v3.py`; `git diff --exit-code -- portability/srp_history_v3/*.csv portability/srp_history_v3/srp_hu_history_v3.oppl portability/srp_history_v3/preflop_srp_history_v3.oppl`; `(cd portability/srp_history_v3 && sha256sum -c HIST3_SHA256SUMS.txt)`.
- 31 testes novos; 344 acumulados esperados. O source principal é [preflop_srp_history_v3.oppl](portability/srp_history_v3/preflop_srp_history_v3.oppl), não modificar v1/v2. Fonte de ação executável é OpenPPL; Python apenas gera/testa.
- **Falha histórica real detectada:** `OpponentCalledOnFlop/Turn` não é verdadeiro após vilão já ter apostado; helpers R/H v2 eram inadequados. V3 corrige consumo R/H e bloqueia alias IP M sem evidência `Set user`. Na instalação OH, confirmar reset/call flags e ação final em replay offline, inclusive `BotsLast...Action`/counters por órbita e fallback.
- Próximo checkpoint: ligar observação cronológica e histórico resolvido às decisões, depois expandir por textura/SPR/betsizes/potes complexos, mantendo o alvo de bot completo. G1/G2-a/G6 não foram promovidos.

**Métrica de cobertura HIST-v3 (ADR-027):** consultar [HIST3_ROUTING_COVERAGE.csv](portability/srp_history_v3/HIST3_ROUTING_COVERAGE.csv) e [routing_coverage.py](portability/srp_history_v3/routing_coverage.py). 484 histórias legais, **100/484 admitidas somente por modelo de fonte**, 264 flop e 120 turn sem roteamento; ação final não demonstrada em OH. Comandos: `python portability/srp_history_v3/routing_coverage.py`; `git diff --exit-code -- portability/srp_history_v3/HIST3_ROUTING_COVERAGE.csv`. Checkpoint agora **36 testes, total CI 349**; atualizar documentação/CSV ao evoluir os predicados, não apenas incrementar contagens.

## Retomada OBRIGATÓRIA — piso R10d e 3bet HU
1. Ler [benchmarks/r10d_floor/README.md](benchmarks/r10d_floor/README.md), [matriz de 14 gates](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv) e [relatório atual](benchmarks/r10d_floor/CURRENT_GAP_REPORT.json); o programa NÃO superou R10d. R10d exato medido: 6.021 WHEN, 1.561 Sets, 561 símbolos user_.
2. Ler [portability/p3bet_hu_v1/README.md](portability/p3bet_hu_v1/README.md); `preflop_srp_and_3bet_hu_draft.oppl` é o arquivo mais recente da estratégia integrada, **não compilado** em OpenHoldem; anteriores preservados.
3. Rodar `python -m unittest discover -s portability/p3bet_hu_v1 -p 'test_*.py' -q`; `python portability/p3bet_hu_v1/build_p3bet_hu.py`; `python -m unittest discover -s benchmarks/r10d_floor -p 'test_*.py' -q`; `python benchmarks/r10d_floor/comparison.py`; verificar `git diff --exit-code` dos artefatos regenerados; manifestos SHA nos dois diretórios.
4. **Esperado:** +27 testes, 376 totais. `comparison.py --release-check` deve retornar 2/BLOCKED nesta etapa; não pôr comando de release-check como step verde da CI.
5. Próximo trabalho: priorizar cobertura real de potes multiway (3way), limped/iso, 4bet, stack bands, ação cronológica e OpenHoldem offline. Não copiar R10d sem verificar semântica, não esquecer o contrato novo nem editar ranges v0.6.1 para mascarar gaps.

## Retomada da SRP 3-way (ADR-030)
- **Arquivo integrado mais recente:** `portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl`, a partir do arquivo P3BET-HU-v1; não editar o histórico e não tomar a nova fonte como executável validado.
- Reproduzir `python -m unittest discover -s portability/p3way_srp_v1 -p 'test_*.py' -q`; `python portability/p3way_srp_v1/build_threeway.py`; verificar `git diff --exit-code -- portability/p3way_srp_v1/preflop_coldcall_intent.oppl portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl`; `(cd portability/p3way_srp_v1 && sha256sum -c P3WAY_SRP_SHA256SUMS.txt)`.
- Após gerar 3way, recomputar `python benchmarks/r10d_floor/comparison.py` e conferir diff/manifesto do benchmark. 16 novos testes (392 totais previstos), contadores de origem e guardas devem se manter. **Benchmark continua NOT MET**, 14/14 requisitos sem validação integral.
- Recomendar expansão das familias faltantes multiway 3way→HU, 4–6 active, limp/iso, 4bet/5bet, históricos e board/runout/SPR, sem inferir superioridade por contagens de código.

## ADR-031: preserve a correção de nuts
Arquivos correntes `portability/p3bet_hu_v1/preflop_srp_and_3bet_hu_draft.oppl` e `portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl`; 41/33 ações novas. Rerodar generators, 15/16 testes de ambos, 12 benchmark, regeneração e SHA. Testes obrigatórios: nuts frente a overbet >250% do pote nunca segue Fold residual. Última fonte 733 WHEN. R10d gate NOT MET; G6 runtime pendente.

## Handoff — Multiway-v2 + LIMP-BB-v1 (20/11/2026)
- Fonte mais nova: `portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl`; pai: `portability/multiway_v2/preflop_multiway_v2_draft.oppl`. **Nunca voltar a fonte anterior ao adicionar próximo módulo.**
- Rodar da raiz: `python -m unittest discover -s portability/multiway_v2 -p 'test_*.py' -q` (25); `python -m unittest discover -s portability/limped_bb_v1 -p 'test_*.py' -q` (17), depois `python portability/multiway_v2/build_multiway_v2.py`, `python portability/limped_bb_v1/build_limp_bb.py` e `python benchmarks/r10d_floor/comparison.py`.
- Verificar hashes nos dois pacotes e em `benchmarks/r10d_floor/BENCHMARK_SHA256SUMS.txt`; verificar `git diff --exit-code` dos integrados e relatórios. Esperado 899 WHEN, 106 funções, 187 listas, 92 SET, 9 user_; 434 testes CI.
- M04/M06 PARTIAL, 14 capacidades não aprovadas, zero OHReplay alvo. **Próximo trabalho:** quedas intermediárias de jogadores, limp/iso, 3bet multiway, depois 4bet/5bet e pós-flop com SPR/board.

## Checkpoint operacional de código — MWT3 → MLIMP2 → P3BMW1
- **Fonte integrada mais recente:** [preflop_srp_limp_3bet_multiway_draft.oppl](portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl).
- Gerar, nesta ordem: `python portability/multiway_transitions_v3/build_transitions_v3.py`; `python portability/multilimp_bb_v2/build_multilimp.py`; `python portability/p3bet_multiway_v1/build_3bet_multiway.py`; `python benchmarks/r10d_floor/comparison.py`.
- Testar: `python -m unittest discover -s portability/<multiway_transitions_v3|multilimp_bb_v2|p3bet_multiway_v1> -p 'test_*.py' -q` (executar separadamente em shell) e `sha256sum -c` dos manifestos locais. Conferir `git diff --exit-code --` dos fontes gerados e matriz benchmark.
- +38 testes, 521 esperados na CI, 1.460 WHEN integrados. **Não** reescrever fontes v0.6.1 nem afirmar R10d superado ou uso em mesa real. Próximas famílias: isolation vs limps, squeeze e 4bet/5bet; board, SPR, perfis e replays continuam pendentes.

**Errata de contagem CI (20/11/2026):** [registro verificável](CI_TEST_COUNT_ERRATA.md). Antes deste bloco: 483 execuções, 471 testes distintos; após: 521 execuções, 509 distintos. A suíte do benchmark R10d com 12 testes roda duas vezes. Registros anteriores de 434/472 eram estimativas incorretas. Essa correção é exclusivamente documental e NÃO altera a estratégia.

## Handoff ISO-1 (DRAFT — 20/11/2026)
- Branch de trabalho `work/iso-v1-draft-20261120`; fonte em `portability/iso_raise_v1/` (handlist, pré-flop, topologia, pós-flop, interpretador, testes e gerador). Pai congelado: `portability/p3bet_multiway_v1/preflop_srp_limp_3bet_multiway_draft.oppl`.
- Executar 13 testes via `python -m unittest discover -s portability/iso_raise_v1 -p 'test_*.py' -q`; executar builder e `git diff --exit-code -- portability/iso_raise_v1/iso_integrated_draft.oppl`. Não mesclar/promover em caso de falha. A CI aprovada [44853164836](https://github.com/pmartins87/Heuristic6max/actions/runs/44853164836) comprovou 534 execuções em 27 suítes e 522 testes deduplicados por suíte, incluindo 13 novos.
- Próximo passo: reconciliar aprovação de CI já verificada e benchmark R10d; depois validar portabilidade em OpenHoldem offline. G2-a HOLD; não alterar v0.6.1 nem iniciar VS_4BET sem nova decisão. O integrado é rascunho e não deve ser usado com dinheiro.

## Handoff BLISO-2 — 13 contextos de blinds (20/11/2026)
- Branch de trabalho `work/blind-iso-v2-draft-20261120`; pai `portability/iso_raise_v1/iso_integrated_draft.oppl`; arquivo integrado DRAFT `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`. Leia o [README do BLISO-2](portability/blind_iso_v2/README.md) e as novas seções no `DECISIONS.md` e `ROADMAP.md` antes de alterações.
- Rodar: `python -m unittest discover -s portability/blind_iso_v2 -p 'test_*.py' -q`; `python portability/blind_iso_v2/build_blind_iso.py`; `git diff --exit-code -- portability/blind_iso_v2/blind_iso_integrated_draft.oppl`; `(cd portability/blind_iso_v2 && sha256sum -c BLISO2_SHA256SUMS.txt)`. Conferir benchmark R10d e SHA dos manifestos. **18 testes novos aprovados** no [workflow 44858080418](https://github.com/pmartins87/Heuristic6max/actions/runs/44858080418), 552 execuções / 540 deduplicadas em 28 suítes, conforme log do job.
- G1/G6 exigem replay OH real offline; G2-a HOLD e VS_4BET não desenvolvido. Próximo incremento: defender isolamento e coldcall/squeeze com origem inequívoca; não publicar cash bot.

## Handoff ISODEF-1 — fonte ativa e portabilidade bloqueada
- **Branch `work/iso-defense-v1-draft-20261121`, PR #8**; origem `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`. O candidato mais recente é `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`. Consultar [README do módulo](portability/iso_defense_v1/README.md), [ADR-038](DECISIONS.md), ROADMAP e PROJECT_STATE antes de mexer em qualquer regra.
- Reproduzir: `python -m unittest discover -s portability/iso_defense_v1 -p 'test_*.py' -q`; `python portability/iso_defense_v1/build_defense.py`; `git diff --exit-code -- portability/iso_defense_v1/iso_defense_integrated_draft.oppl`; `(cd portability/iso_defense_v1 && sha256sum -c ISODEF1_SHA256SUMS.txt)`; `python benchmarks/r10d_floor/comparison.py`, diff do relatório e SHA256 do benchmark.
- **21 novos testes aprovados** na [workflow 44860943038](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038) (573 execuções, 561 deduplicadas por suíte, 29 suítes). Campos `Raises`, `Calls`, `FirstRaiserPosition`, `LastRaiserPosition`, `StillToAct` e tags ainda exigem OH offline e confirmação da ação final. G1 ABERTO, G2-a HOLD, G6 PENDENTE; 0/14 R10d VERIFIED. Sem operação real.
