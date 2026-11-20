# Histórico consolidado — Heuristic6max

- **v0.1:** arquitetura inicial, 22 testes.
- **v0.2:** reconstrutor sintético + RFI 5 × 169, 71 testes.
- **v0.3:** VS_OPEN 15 × 169, 91 testes.
- **v0.4:** VS_3BET 15 × 169, 114 testes; 8 divergências maiores frente a benchmark não comparável.
- **v0.5:** decomposição por mão sem mudar as ações v0.4; 119 testes; 51 arquivos, agora totalmente importados no GitHub.
- **v0.6 (20/11/2026):** correção *de medição* de VS_3BET com card removal e modelo de 3-bet VS_OPEN. 15 nós, 1.326 combos físicos, 124 testes, 61 arquivos no snapshot completo. Mudança de frequências auditadas: -0,409 a -1,766 p.p. em 4bet condicional. **Nenhuma ação estratégica foi alterada; G2-a permanece HOLD.**

Consulte [DECISIONS.md](DECISIONS.md) para justificativas e [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md) para hashes e commits. Não confunda teste de infraestrutura com validação GTO.

- **v0.6.1 (20/11/2026):** hotfix do teste de integridade após falha do primeiro GitHub Actions: 50 fontes ancestrais idênticas, 1 manifesto regenerado. 124 testes mantidos; no change in poker decisions. A v0.6 é mantida para auditoria histórica; CI e documentos vivos passaram a apontar para v0.6.1.

- **Auditoria v0.7 (20/11/2026):** 7 novos testes, 15 nós analisados para pressão de 3bet por combo adversário, 8 tabelas de mão agregadas em CSV e medição do limite de blefe isolado de equidade zero. 7/8 nós críticos sob pressão nesse contrafactual; ranges não modificados. Baseline 124 + 7 = 131 testes. Arquivos em [audits/g2a_v0_7/](audits/g2a_v0_7/), sem duplicar ou modificar snapshots históricos.

- **Auditoria v0.8 (20/11/2026):** sem alteração estratégica, cálculo de massa por 169 classes e nove famílias nos 15 confrontos RFI→VS_3BET, ranking das principais fontes de FOLD nos oito críticos, pot odds imediatas e sensibilidade hipotética às cold actions. 11 testes novos, total 142. HJ-CO tem 58,1119 pp de FOLD em quatro famílias de mãos; conclusão de exploração da v0.7 continua apenas contrafactual. Código e quatro CSVs em [audits/g2a_v0_8/](audits/g2a_v0_8/), com manifesto de hashes. G2-a HOLD.

- **Ajuste de reprodutibilidade v0.8 (mesma data):** primeira execução CI falhou apenas porque pesos numericamente empatados foram ordenados em sequências distintas pelo Python 3.13 e 3.11; ajustado desempate pela classe de mão após arredondamento da **chave de ordenação** em 12 casas, sem mudar pesos/ações. Acrescentado teste determinístico (+1). Relatórios e SHA256 regenerados, v0.6.1 intacta.

- **Auditoria v0.9 (20/11/2026):** HJ/CO, 169 classes, análise contrafactual de 15 classes, 36 fronteiras de preço de call/4bet sob rake, sizing e realização hipotéticos; 11 testes novos, **153 no total**. Estratégia v0.6.1 intacta. [Código e relatórios](audits/g2a_v0_9/README.md). Gate G2-a HOLD.

- **Auditoria v0.10 (20/11/2026):** 169 classes físicas de equity de showdown HJ/CO 3bet (fonte externa fornecida, 1.624.350 confrontos, input bruto não republicado por licença desconhecida), checagem Monte Carlo independente de 15 classes × 50k amostras e 10 testes novos (163 acumulados previstos). Nenhuma estratégia alterada. [Código/relatórios](audits/g2a_v0_10/README.md). G2-a HOLD.

- **Auditoria v0.11 (20/11/2026):** gate conservador de compatibilidade de charts externas e registro de procedência de três fontes (ART/GTO, Simple GTO, GTO Wizard). Nenhuma é substituição direta verificada do HJ/CO 3-bet 8 BB com rake/cap desconhecidos. **11 testes adicionais (174 no total)**, CSV determinístico, manifesto SHA256. Critério de parada de auditorias toy-EV sem fatos novos; Python permanece núcleo; OpenPPL é G6 pendente. Nenhum range modificado. [Relatório](audits/g2a_v0_11/README.md).


- **PORT-0 / ADR-016 (20/11/2026):** introduzido contrato de paridade OpenPPL obrigatória para novas decisões executáveis, prova com 2 regras BTN RFI nativas no arquivo .oppl e intérprete de testes Python da mesma fonte; 7 testes, 3.042 estados; total CI esperado 181. Estratégia/ranges intactos; não foi executado no OpenHoldem real. [Contrato](PORTABILITY_CONTRACT.md).

- **PORT-1 parcial (20/11/2026):** 168/169 mãos LJ RFI puras portadas como duas listas+regras nativas OpenPPL (43 raise, 125 fold); KJo 40% raise ficou BLOQUEADO. 15 testes de paridade estática e manifesto SHA256; nenhuma tabela estratégica alterada. Total esperado 196 testes. Gate não aprovado e execução OH real pendente. [Fonte](portability/port1/README.md).
