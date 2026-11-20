# Manifesto de releases (20/11/2026)

Os seguintes hashes SHA-256 foram calculados sobre os **ZIPs locais efetivamente existentes**; presença neste documento NÃO significa que os ZIPs estejam hospedados no GitHub.

| Versão | ZIP | SHA-256 |
|---|---|---|
| v0.1 | `GTO_Heuristic_6Max_v0.1_Arquitetura_Contrato_Testes.zip` | `92a0f3a847d0eb62d10e35d6d6aa5be45a51b375e72f430168ce53c72a888397` |
| v0.2 | `GTO_Heuristic_6Max_v0.2_G1_G2_RFI_DRAFT.zip` | `d864c3f9dd2c7699dcba17c9b27c6c3f5cc87f0def89fa845b4cec7a912abf52` |
| v0.3 | `GTO_Heuristic_6Max_v0.3_G2_VS_OPEN_DRAFT.zip` | `ec6ca7de7a10893e9dbb8bc18baabd3404f69e0435b02af755e0229650b6d552` |
| v0.4 | `GTO_Heuristic_6Max_v0.4_VS_3BET_DRAFT.zip` | `6086ccc8b7b4aae583d831287643cfc8f6330769ab96c5d901fdefd63279e227` |
| v0.5 | `GTO_Heuristic_6Max_v0.5_Auditoria_Composicao_Handoff.zip` | `7b036634896c560fbc7e4a1794f981860fdd9a065bf3161abb0698b6bf97022a` |

## Estado de replicação

- **GitHub confirmado:** arquivos vivos de documentação, README v0.4 arquivado, resumos VS_3BET e auditoria v0.5, script de verificação.
- **Pendente (Issue #1):** importar o diretório completo `gto6_heuristic_v0_5/`, que contém 51 arquivos, inclusive 22 módulos Python herdados, testes, CSV de 2.535 linhas e `SHA256SUMS.txt`.
- Ao importar, verificar SHA de cada arquivo listado no `SHA256SUMS.txt` do pacote. A versão futura deve criar novo manifesto se alterar conteúdo.
- Não confundir PASS em 119 testes sintéticos com validação estratégica GTO ou replay de OpenHoldem.

Ver [estado atual](PROJECT_STATE.md) e [bloqueio de sincronização](https://github.com/pmartins87/Heuristic6max/issues/1).
