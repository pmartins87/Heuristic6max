# G2-a v0.11 — Gate de admissibilidade de charts e status OpenPPL

**20/11/2026 — auditoria incremental, sem alterar estratégia ou criar bot operacional.**

## Decisão e motivo

As auditorias v0.7–v0.10 confirmaram vulnerabilidades hipotéticas e equidade bruta do HJ contra 3-bet do CO, mas **não** provaram EV ou uma ação superior. Continuar extrapolando cenários econômicos sem dados de rake/cap, EQR calibrada e fonte solver comparável possui rendimento decrescente. A partir deste checkpoint, o gate **para de gerar novos candidatos de call/4bet por percentuais isolados**. Antes de revisar ranges, exige configuração econômica ou referências com proveniência, sizing e árvore adequados.

Este trabalho **não é uma mudança automática para charts externas**. Introduz um teste estrito de compatibilidade para avaliar a possibilidade futura de incorporá-las; as regras de preferência por referência validada **ainda não são executadas pela estratégia Python e não são código OpenPPL**.

## Cenário alvo verificado no código

- NLHE cash 6-max, stack ~100 BB, HJ RFI **2,5 BB**, CO 3-bet **8,0 BB**, Hero HJ responde fora de posição.
- Rake efetivo e cap da plataforma **DESCONHECIDOS**. Valor ausente não vira rake zero.
- As três tabelas RFI, VS_OPEN e VS_3BET de v0.6.1 continuam **DRAFT**.

## Fontes públicas examinadas

| Fonte | Evidência pública verificada | Limite de uso no nó alvo |
|---|---|---|
| [ART/GTO HJ RFI](https://artgto.com/learn/ranges/mp/open/) | HJ open 2 BB em 100 BB; permissão de estudo/uso pessoal indicada na página | Não é defesa VS_3BET HJ/CO, sizing diferente. Não inferir licença de republicação nem utilização comercial |
| [Simple GTO Cash Bundle](https://simplegto.com/products/cash-bundle) | Estrutura publicada 100 BB: open 2,5 BB e 3-bet 3,4× em posição; rake identificado como 500z | 3,4× implica **8,5 BB**, mas a existência deste sizing no nó exato não foi comprovada; solução/licença e detalhes de rake requerem confirmação |
| [GTO Wizard](https://lp.gtowizard.com/) | Soluções pré-flop cash 6-max disponibilizadas em interface | Nó exato, rake, sizings, acesso exportável e permissões **não verificados** |

O código `source_gate.py` lê `source_candidates.json`, compara contrato econômico, configurações da árvore, evidência da classe de nó e direitos de utilização, gerando `SOURCE_APPLICABILITY_v0_11.csv`. As três fontes ficam **REFERENCE_ONLY** neste momento, não por serem ruins, mas por **não terem todas as condições verificadas**.

Em uma fonte futura perfeita e licenciada, a resposta seria apenas `ELIGIBLE_FOR_MANUAL_REVIEW`. Isso **não autoriza copiar nem executar suas ações automaticamente**.

**IMPORTANTE:** ART/GTO também tem charts de defesa a 3-bet, mas a página examinada é especificamente o RFI HJ e por isso foi registrada como nó diferente; não se pode concluir que *toda* a biblioteca ART/GTO seja incompatível.

## Status de OpenPPL (o usuário perguntou se está sendo desenvolvido nele)

O projeto atualmente executa o motor de referência e auditorias em **Python**. Nenhum arquivo `.oppl` foi encontrado na árvore GitHub do checkpoint anterior; os contratos v0.6.1 não foram validados contra replays reais do OpenHoldem. **G6 — adaptação OpenPPL/OpenHoldem — permanece PENDENTE**, incluindo tradução de ações, semântica dos símbolos, proteção contra estados desconhecidos e smoke-tests. Não antecipar conversão antes de estabilizar a estratégia e a leitura dos estados.

## Gates de decisão e critérios de parada

1. **G2-a HOLD**: Não substituir charts nem modificar frequências antes de: node/stack/sizing/rake-caps compatíveis, permissão adequada e checagem de EV/qualidade ou aproximação justificada.
2. **G1 aberto**: coletar/reconstruir replays reais em ambiente de teste sem apostas para verificar a observação. Não inferir G1 concluído pelos testes sintéticos.
3. **G2-b bloqueado**: VS_4BET não começa automaticamente.
4. **G6 pendente**: sem arquivo OpenPPL executável; tradução futura deve refletir contrato Python validado, não uma estratégia paralela.
5. **Parada de auditorias sintéticas HJ-CO**: não repetir cálculos ilustrativos de rake/EQR até haver evidência/hipótese externa concreta que mude a decisão; utilizar trabalho existente v0.7–v0.10.

## Reprodutibilidade

```bash
python -m unittest discover -s audits/g2a_v0_11 -p 'test_*.py' -q
python audits/g2a_v0_11/source_gate.py
cd audits/g2a_v0_11 && sha256sum -c AUDIT_SHA256SUMS.txt
```

A tabela de fonte é **metadado explicativo, não dados proprietários de ranges**. A metodologia e os termos dos terceiros podem mudar, portanto as evidências devem ser conferidas novamente antes da adoção.
