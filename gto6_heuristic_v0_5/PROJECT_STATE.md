# Estado atual — Heuristic6max

Data de referência: **20/11/2026** | Versão de trabalho: **v0.5** | Status: **HOLD / NÃO OPERACIONAL**

## Hipóteses de estudo
6-max cash NLHE, 100 BB alvo (95–105), blinds 0,5/1, sem ante. RFI 2,5 BB em LJ–BTN, SB 3 BB; sizings de 3bet fixos. Linhas sem limpers, sem caller intermediário, sem shove e sem sizing diferente. Rake não calibrado. Estas condições NÃO representam todas as mesas de cash.

## Inventário e evidência
- RFI: 845 linhas (5 posições × 169 classes), v0.2, DRAFT.
- VS_OPEN: 2.535 linhas (15×169), v0.3, DRAFT.
- VS_3BET: 2.535 linhas (15×169), v0.4, DRAFT (888 classes alcançáveis, 1.647 inatingíveis a partir do RFI).
- v0.5: detalhamento de 2.535 contribuições por mão e 15 resumos da composição, **sem trocar ações estratégicas**.
- 119 testes em Python aprovados nesta sessão; apenas simulação sintética, sem replays reais OpenHoldem e sem validação de EV.
- Problemas conhecidos: 8/15 comparadores de VS_3BET divergem >8 p.p., 4/15 divergem 4–8 p.p., 3/15 ≤4 p.p.; estruturas de comparação não iguais. O G1 exige observações reais.

## Bloqueios
1. Revisar criticamente as classes de mãos nos oito nós principais, sem calibrar cegamente agregados externos.
2. Modelar condicionamento à faixa de 3bet adversária e card removal antes de inferir EV ou frequência ótima.
3. Validar replays reais e mapear erros de scrape; `None` não significa fold nem check.
4. Replicar código e datasets deste pacote no repositório GitHub; documentação sem arquivos executáveis ainda é um checkpoint **incompleto**.

## Próximo passo técnico
Auditar `SB vs BB`, `HJ vs CO`, `LJ vs CO`, `CO vs BTN` por classes e requisitos de posição/rake/árvore, depois os quatro outros `MAJOR_REVIEW`. Só então avaliar mudar frequências, e só depois iniciar VS_4BET.

## Próxima ação do usuário
Se os fontes/datasets ainda não estiverem no GitHub, subir o ZIP extraído para o repositório (sem apagar os documentos vivos) para permitir continuidade independente deste chat. Não executar estratégia em mesa.
