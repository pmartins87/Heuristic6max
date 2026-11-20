# VS_OPEN-MVP — pré-flop 6-max em OpenPPL, 15 confrontos

**Checkpoint:** 20/11/2026. **Objetivo:** tornar a heurística existente jogável em termos de regras pré-flop, **sem criar um solver nem recalcular ranges**. **Ainda NÃO é um bot operacional**, não foi compilado/testado no OpenHoldem-alvo e não cobre toda a árvore de apostas.

## Entrega prática

- `vs_open_6max_mvp.oppl`: VS_OPEN completo (15 confrontos × 169 classes = **2.535 decisões**), **81 handlists sem sobreposição por confronto**, **121 regras WHEN**. Política originária exclusivamente da `gto6_heuristic_v0_6_1/vs_open_reference.py` histórica. Os valores não foram alterados, apenas transcritos por geração determinística.
- `preflop_rfi_vsopen_draft.oppl`: **arquivo OpenPPL combinado** do RFI-MVP anterior com VS_OPEN; **uma única função `##f$preflop##`**, handlists de namespaces distintos, **142 regras** (21 RFI + 121 VS_OPEN). Esse arquivo é um *rascunho de integração* e não deve ser executado em mesa real.
- `generate_vs_open_mvp.py`: gerador **offline** de OpenPPL e CSV, não é dependência em runtime.
- `vs_open_source_interpreter.py`: parser/interpretador de testes que lê **o próprio `.oppl`**; não contém tabelas estratégicas paralelas. Emulamos apenas o subconjunto documentado e testado, sem fingir executar o OpenHoldem.
- `VS_OPEN_2535_MAPPING.csv`: índice auditável das ações, tamanhos e probabilidades originais.
- `test_vs_open_mvp.py`: **19 testes novos**, incluindo 2.535 classes em quatro valores de sorteio, limites de misturas, conflitos de precedência e testes negativos de guardas, OpenPPL integrado e integridade. Total previsto na CI: **273 = 254 anteriores + 19**.
- `VS_OPEN_MVP_SHA256SUMS.txt`: integridade SHA-256 dos outros arquivos deste diretório.

## Contexto coberto

**Cash 6-max; primeiro RFI do adversário e zero callers**; stacks entre 95–105 BB como no projeto, pot inicial com blinds de 0,5/1 e sem ante; abertura do agressor para 2,5 BB LJ–BTN ou 3 BB SB. **Nenhum squeeze, limper, caller intermediário, 4bet, segundo orbit ou postflop.**

As guardas OpenPPL incluem `IsPreflop`, `nplayersdealt = 6`, posição Hero, `Raises = 1`, `Calls = 0`, `FirstRaiserPosition`, `LastRaiserPosition`, `PotSize = 4`, `AmountToCall`, stacks e flag `StackUnknown`. O manual fornecido define as posições relativas ao big blind da **primeira órbita**: LJ 5, HJ 4, CO 3, BTN 2, SB 1. O valor no executável de destino requer confirmação com replays, porque scraping e primeira/última ação podem estar incompletos.

`AmountToCall` esperado: **2,5 BB** em assentos sem blind, **2 BB** no SB versus open de 2,5, **1,5 BB** no BB versus open de 2,5 e **2 BB** no BB versus open de SB 3. O pote antes da ação é 4 BB nos 15 confrontos. Tamanhos de 3-bet `RaiseTo` preservados: **8 BB** em posição, **10,25 BB** fora, e **9,6 BB** no BB versus SB, exatamente conforme a política atual. **São tamanhos finais (`RaiseTo`), não acréscimos (`RaiseBy`).**

## Massa de classes, não GTO comprovada

| Ação/bucket | Quantidade de classes nos 15 confrontos |
|---|---:|
| 3BET puro | 129 |
| CALL puro | 310 |
| FOLD puro | 1.822 |
| 3BET/CALL misto | 59 |
| 3BET/FOLD misto | 154 |
| CALL/FOLD misto | 61 |
| **Total** | **2.535** |

As misturas são implementadas com `randomhand < limiar` e `randomhand >= limiar`, com o mesmo valor da mão nas reavaliações. Assim, nenhum RNG Python é necessário no motor OpenPPL. Não assumimos independência das decisões em nós diferentes de uma mesma mão. Todos os buckets são **mutuamente exclusivos por mão**; conflitos já existentes entre grupos seed CALL e 3BET preservam **precedência 3BET** após expansão do snapshot, sem atribuir ações duplicadas.

## Riscos de integração (não transformar em pesquisa infinita)

1. **Sem paridade OpenHoldem real:** interpretador Python não demonstra execução, disponibilidade de símbolo, sizing final, limites de stack nem estabilidade da observação.
2. **No-match/fallback:** se condição sair do domínio ou scraping falhar, o arquivo não possui fallback seguro; o OpenHoldem pode chamar estratégia padrão. `None` de teste não é garantia de não agir.
3. **Arquivo combinado ainda incompleto:** falta VS_3BET (re-raise sobre nosso open), 4bet, outras situações pré-flop, pós-flop, e teste real de ações no OpenHoldem. Não executar em mesas reais.
4. **Não validamos EV/GTO:** ranges v0.6.1 são hipóteses heurísticas; não foi feita calibração de rake/stack para a plataforma. G2-a continua HOLD para alteração de frequências; isso **não impede desenvolver código sem alterar a estratégia**.

## Como reproduzir

```sh
python -m unittest discover -s portability/vs_open_mvp -p 'test_*.py' -q
python portability/vs_open_mvp/generate_vs_open_mvp.py
git diff --exit-code -- portability/vs_open_mvp/vs_open_6max_mvp.oppl portability/vs_open_mvp/preflop_rfi_vsopen_draft.oppl portability/vs_open_mvp/VS_OPEN_2535_MAPPING.csv
(cd portability/vs_open_mvp && sha256sum -c VS_OPEN_MVP_SHA256SUMS.txt)
```

**Próximo passo prático:** portar **VS_3BET v0.6.1** em OpenPPL e integrar ao mesmo `##f$preflop##`, mantendo a ressalva de G2-a HOLD (não alterar frequências). Antes de promover a versão para uso operacional, resolver fallback e executar alguns replays sem apostas no OpenHoldem-alvo (PORT-3b / G1). Não iniciar estratégia pós-flop nem G2-b sem tratar esses requisitos.
