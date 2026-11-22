# V2/PILOT-01 — duas ações, fonte OpenPPL nativa isolada

**Data:** 21/11/2026. **Estado:** `F3_DRAFT_SOURCE_ONLY`. Não é uma estratégia completa; **não carregar no OpenHoldem durante jogo**.

[Plano Vivo V2](../PLAN.md) · [Decisões F2 revisadas](../cases/BTN_BB_SRP_CBET_F2_PILOT.md) · [Contrato de contexto F1](../cases/BTN_BB_SRP_FLOP_CBET_SOURCE_CONTRACT.md)

## Fonte única e decisões implementadas

[`f2_two_spots_draft.oppl`](f2_two_spots_draft.oppl) contém duas decisões *por cartas físicas exatas*, sem transplantar as 2.016 regras legadas:

| Caso | Pré-flop de fixture | Flop após BB CHECK | Ação desejada |
|---|---|---|---|
| SPOT-001 | BTN Q♠J♠ RFI 2,5BB; SB fold; BB call | Q♥ Q♣ 6♦ | `BetThirdPot FORCE` (~33,3%) |
| SPOT-002 | BTN A♥5♥ RFI 2,5BB; SB fold; BB call | A♠ 7♦ 3♣ | `Check FORCE` |

Os dois opens de fixture **não** representam a política de BTN ~42% de mãos; são apenas a criação do contexto pré-flop real que permite testar o pós-flop. O restante do range 41–44% e os outros boards continuam não implementados.

## Por que expressões físicas?

O **OpenPPL Manual** fornecido pelo usuário explica `hand$` e `board$`, inclusive cartas com naipe, `Set user...` e `BetThirdPot`. O código-fonte fornecido em `CSymbolEngineOpenPPLHandAndBoardExpression.cpp` mostra comparação de ranks com multiplicidade e verificação de cartas exatas por suit; usar `board$QhQc6d`/ `hand$QsJs` e `board$As7d3c`/`hand$Ah5h` é mais restrito do que um `HaveTrips` ou `HaveTopPair` genérico. O parser avisa que `hand$QJs` (terminação ambígua em spades) deve ser desambiguado; usamos `hand$QsJs`.

O Manual afirma também que `user_...` começa falso e reinicia por mão. A fixture define `user_V2PilotBTNOpen` no **pré-flop não aberto** e exige `BotRaisedBeforeFlop` e `NumberOfRaisesBeforeFlop = 0` no flop. A origem e os atores são adicionalmente cercados por seis jogadores dealt, Hero BTN, posição last, 1 adversário no flop, BB identificado pelo chair, zero aposta a pagar, zero apostas no flop, stack 90–105 BB após o open.

**Atenção:** a correspondência entre `NoBettingOnFlop`, `NumberOfRaisesBeforeFlop`, `headsupchair`, `InButton`, o marker `user_`, os montantes e a ação real **não** foi validada na versão concreta do executável OpenHoldem. O símbolo `Beep FORCE` é um fallback intencional sem ação **somente de laboratório**, não uma política segura de jogo.

## Testes e limite de afirmação

`python -m unittest discover -s v2/pilot_01 -p 'test_*.py' -v`

Quatro testes locais estáticos passaram, e [CI V2 isolada](../../.github/workflows/v2-pilot.yml) também executa exatamente essa suíte em PRs que alterem o piloto; a CI não usa OpenHoldem, checando fonte OpenPPL, duas ações e guardas básicos; **não** simulam o motor C++ nem comprovam parsing, scrape, ação enviada/aceita ou default fallback. O histórico do projeto já demonstrou que testes estáticos verdes podem ocultar erros estratégicos; aqui o respaldo estratégico vem dos estudos profissionais **anteriores** à implementação.

Próximo gate `F3`: carregar em OpenHoldem em replay **desconectado de mesa real**, validar que `QsJs/QQ6r` gera bet de 33% e `Ah5h/A73r` gera check, que outras cartas ou apostas não geram ação perigosa, e que a memória não migra para a mão seguinte. **Não** publicar como bot completo nem habilitar jogo real. O modelo de 42% BTN e árvore pós-flop mais ampla serão incrementos separados.
