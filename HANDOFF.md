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
