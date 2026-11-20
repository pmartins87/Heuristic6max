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
