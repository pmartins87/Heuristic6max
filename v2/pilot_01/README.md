# V2/PILOT-01 — duas ações, fonte OpenPPL nativa isolada

**Data:** 21/11/2026. **Estado ADR-048, preservado por ADR-049:** `F3_STATIC_SYMBOLIC_VERIFIED / OH_PENDING` (20 testes; sem OpenHoldem real). Não é uma estratégia completa; **não carregar no OpenHoldem durante jogo**.

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


## ADR-048 — verificação estática adversarial acrescentada

- [strict_symbolic_replay.py](strict_symbolic_replay.py) avalia condições e a primeira ação verdadeira diretamente da fonte OpenPPL, somente no subconjunto desta fixture; rejeita construções/símbolos não suportados. **Não é o interpretador OpenHoldem**.
- [test_adversarial.py](test_adversarial.py) acrescenta 16 testes e vários subcasos negativos aos 4 testes anteriores: **20 testes em Python local**, nenhum jogo/replay real.
- [OH_OFFLINE_EVIDENCE_GATE.md](OH_OFFLINE_EVIDENCE_GATE.md) separa prova de lógica estática de evidências ainda inexistentes: parser C++ carregando a fórmula, marcador de RFI em mão de verdade, fluxo cronológico, botão real, bet enviada/aceita e comportamento fora do domínio.
- O filtro StackSize cobre o Hero, **não certifica stack efetivo do BB**. Não dizer que a fórmula opera exclusivamente a 100BB efetivos.
- O plano seguinte depende de ManualMode/OHReplay e do build instalado no Windows. Não incrementar a estratégia com regras universais enquanto ainda não sabemos se o primeiro módulo executa corretamente em OH.


## ADR-049 — papel correto deste piloto
Este arquivo e seus dois casos exatos **são fixtures de engenharia**, úteis para testar linguagem/memória e ação final do OpenHoldem em segurança offline. **Não definem escopo do futuro bot, prioridades permanentes, nem necessidade de refinar 41–44% BTN.** A trilha estratégica deve estudar **muitas outras famílias de estados** em paralelo, conforme [Política Geral](../GENERAL_POLICY.md), [auditoria DeepCrusher](../DEEPCRUSHER_TRANSFER_AUDIT.md) e [nova família F1](../families/DEFENDING_VS_AGGRESSION_F1.md). Falta replay OH real para promover a **execução** desta fixture, não para continuar a **pesquisa estratégica** de outros módulos.
