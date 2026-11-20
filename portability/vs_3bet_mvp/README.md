# VS_3BET MVP — respostas a 3-bet em OpenPPL (15 confrontos)

**Checkpoint 20/11/2026. Módulo estratégico DRAFT; não é um bot operacional.**

## Objetivo e resultado prático

O bot heurístico cash 6-max, em torno de 100 BB, já tem RFI e VS_OPEN convertidos para OpenPPL. Esta etapa incorpora **VS_3BET**: nós em que o Hero abriu primeiro (LJ, HJ, CO, BTN ou SB) e sofreu uma única 3-bet de um adversário elegível, sem callers/limpers/squeeze, com sizing exatamente previsto na v0.6.1.

- **15 confrontos × 169 classes = 2.535 linhas examinadas**.
- **888 combinações de classe/confronto alcançáveis** depois de uma abertura RFI (inclusive RFI misto de KJo etc.); **1.647 não alcançáveis** (`NOT_REACHABLE_FROM_RFI`). Um estado impossível **não** vira fold arbitrário.
- **90 handlists + 135 regras** em `vs_3bet_6max_mvp.oppl`, cobrindo 4bet pura, 4bet/call, 4bet/fold, call puro, call/fold e fold puro. Todas as misturas são por `randomhand` constante na mão, com dois ramos complementares. 4bets usam `RaiseTo` em BB, jamais `RaiseBy` ou shove.
- O **arquivo combinado** `preflop_rfi_vsopen_vs3_draft.oppl` contém **uma única função `##f$preflop##`**, com os **142 ramos anteriores** (RFI/VS_OPEN) **mais 135 novos**, total **277 regras**, sem substituir nenhum histórico.
- Não houve mudança nas frequências, nas mãos, nos sizings ou no baseline `gto6_heuristic_v0_6_1`.

## Compatibilidade OpenPPL: escolhas explícitas

Consultados os manuais do projeto `OpenPPL Manual.pdf` (especialmente *History Symbols*, *Position Symbols* e *Betsizes And Stacksizes*) e fonte integrada OpenHoldem. A implementação **não é tradução Python no runtime**: as decisões estão exclusivamente em handlists e `WHEN` OpenPPL. `vs3_source_interpreter.py` lê literalmente essas mesmas regras para testar, sem outras ranges.

- `Raises = 1` porque o OpenPPL conta **raises de oponentes** na rodada; o RFI do Hero não conta. `BotRaisedBeforeFlop` e `RaisesSinceLastPlay = 1` distinguem o cenário de uma 3-bet da simples resposta VS_OPEN. `FirstRaiserPosition` deve ser o Hero; `LastRaiserPosition` deve ser o vilão 3bettor.
- Exige o pote e `AmountToCall` conforme **a 3bet exata** da v0.6.1. Outros tamanhos ficam fora do módulo; o OPPL não improvisa a resposta.
- Usa `StackSizeAtBeginningOfCurrentRound` em vez de `StackSize` para verificar 95–105 BB, pois o Hero **já investiu dinheiro ao abrir**. `MinOpponentStackSize` e `MaxOpponentStackSize` também são guardas da hipótese de stacks perto de 100 BB.
- Não usa `StillToAct` (documentado como restrito à primeira órbita) para validar a **segunda decisão do Hero**.
- As cinco classes cujo RFI anterior usa mix (`LJ KJo`, `HJ QJo`, `BTN 53s`, `SB K3s`, `SB 97o` não é RFI raise) **não** recebem uma segunda mistura de VS_3BET. As classes abertas parcialmente que chegam ao nó de VS_3BET fazem FOLD puro na baseline, evitando correlação condicional adicional do mesmo `randomhand` nesse cenário.

**Advertência crítica de integração:** os contadores, posições históricas e stack inicial precisam ser medidos no executável OpenHoldem do usuário. O manual informa que os contadores dependem de ações estáveis do autoplayer; no modo manual, os valores podem ser diferentes ou indisponíveis. `FirstRaiserPosition`/`LastRaiserPosition` possuem limitação documental de primeira órbita. O arquivo pode passar nos testes Python e **não** funcionar na engine OpenPPL real. O OpenHoldem também possui `default.bot` e substituições automáticas de ação quando ela é ilegal. Portanto **não carregar em mesas com dinheiro real** nem afirmar validação de paridade ou GTO.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `vs_3bet_6max_mvp.oppl` | Fonte de decisão OpenPPL, 90 handlists / 135 regras |
| `preflop_rfi_vsopen_vs3_draft.oppl` | Arquivo único, 277 regras, RFI + VS_OPEN + VS_3BET |
| `VS3_2535_MAPPING.csv` | 2.535 casos; expõe os 888 alcançáveis / 1.647 não alcançáveis |
| `generate_vs3_mvp.py` | Gerador OFFLINE a partir de `vs_3bet_reference.py` v0.6.1 |
| `vs3_source_interpreter.py` | Intérprete restrito da MESMA fonte OpenPPL para testes, não bot |
| `test_vs3_mvp.py` | 23 testes de mapeamento, mixes, preço, guardas, histórico, integridade e merge |
| `VS3_MVP_SHA256SUMS.txt` | Manifesto de integridade dos demais arquivos |

## Comandos rápidos de verificação

```sh
python -m unittest discover -s portability/vs_3bet_mvp -p 'test_*.py' -q
python portability/vs_3bet_mvp/generate_vs3_mvp.py
git diff --exit-code -- portability/vs_3bet_mvp/*.oppl portability/vs_3bet_mvp/*.csv
(cd portability/vs_3bet_mvp && sha256sum -c VS3_MVP_SHA256SUMS.txt)
```

**Teste local:** 23/23 concluídos. **Total esperado em CI:** 277 testes (254 já versionados + 23 novos). O pacote não altera estratégia, não prova winrate e não exige resolver GTO por cálculo.

## Próxima entrega, sem ciclos de auditoria infinitos

O pré-flop agora possui os três núcleos já existentes convertidos em OPPL, mas continua parcial: faltam limps externos, squeezes, outros sizings e stacks, VS_4BET/5BET e pós-flop. **G2-a permanece DRAFT/HOLD para qualidade estratégica**, e G2-b segue bloqueado; não confundir conversão de código com validação do range.

Avançar com uma **política explícita de lacunas e observação mínima no OHReplay/ManualMode offline**, evitando que ausência de regra dispare `default.bot` silenciosamente. Depois implementar o primeiro núcleo pós-flop SRP HU usando heurísticas e símbolos nativos OPPL. Não é necessário comprovar equilíbrio de Nash nem construir um solver.
