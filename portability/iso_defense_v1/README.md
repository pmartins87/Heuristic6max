# ISODEF-1 — defesa contra isolation raise (DRAFT, não operacional)

**Escopo intencionalmente pequeno:** dois cenários distintos de `VS_OPEN` — existe **um limp anterior** ao isolamento adversário, mas nenhum outro caller do raise. Evita introduzir uma defesa genérica com `Calls`/histórico ainda não confirmados em OpenHoldem.

| Hero | Agressor de isolamento | Modelo anterior à ação | Sizing |
|---|---|---|---|
| BTN | CO (após um LJ/HJ limp) | `Raises=1`, `Calls=1`, `First/LastRaiserPosition=3`, `PotSize=7 BB`, `AmountToCall=4.5 BB`, `StillToAct=2` | 3-bet a **13.5 BB** |
| BB | BTN (após um limp em posição anterior) | `Raises=1`, `Calls=1`, `First/LastRaiserPosition=2`, `PotSize=7 BB`, `AmountToCall=3.5 BB`, `StillToAct=0` | 3-bet a **15.75 BB** |

Assumem-se seis jogadores dealt, sem antes, blinds 0.5/1 BB, stacks iniciais aproximadamente 100 BB, nenhum caller pós-isolamento e nenhum re-raise até a primeira decisão do Hero. Os sinais `Calls`, `StillToAct`, `First/LastRaiserPosition` e o pote exato continuam hipóteses **a verificar no executável-alvo**; potes 7 BB são uma modelagem, não captura real.

## Ações e ranges isolados

São três novas handlists, **sem tocar** a estratégia v0.6.1, ISO-1 ou BLISO-2:
- `listH6DEF3BET`: **AA KK QQ AKs AKo**, nos dois cenários.
- `listH6DEFCALLBTN`: **JJ TT 99 AQs AJs KQs QJs**.
- `listH6DEFCALLBB`: **JJ TT AQs AJs KQs**.

As demais classes recebem `Fold FORCE` **somente nesses dois domínios exatos**. Os quatro tags `user_H6_DEF_{BTN3,BTNC,BB3,BBC}` são intenções de 3-bet ou call, não confirmação do clique do motor. `defense_preflop_capture.oppl` contém as ações; o interpretador as **lê** da fonte.

## Pós-flop

`defense_policy.oppl`: **42 decisões** (16 flop, 14 turn, 12 river), separando 3bettor de coldcaller, HU e dois adversários, com proteção `HaveNuts` contra overbets. `defense_topology.oppl`: **12 topologias cronológicas** (3 flop, 4 turn, 5 river), incluindo eliminação de um oponente durante uma street. O pós-flop só entra se houver *uma* tag, nenhum tag ancestral de outro tipo de pote, `NumberOfRaisesBeforeFlop=1`, ausência de all-in, e as flags nativas `BotRaisedBeforeFlop/BotCalledBeforeFlop` coerentes. O número de oponentes no flop deve ser 1–2; 4-way+, squeezes e novas 4bets ficam fora.

**Os limites de preço, ranges e sizes são heurísticas novas sem calibração de EV e não constituem um chart GTO.** A ausência de combinação no intérprete (`None`) não garante fallback legal no OpenHoldem.

## Reprodução de artefatos

```bash
python -m unittest discover -s portability/iso_defense_v1 -p 'test_*.py' -q
python portability/iso_defense_v1/build_defense.py
git diff --exit-code -- portability/iso_defense_v1/iso_defense_integrated_draft.oppl
(cd portability/iso_defense_v1 && sha256sum -c ISODEF1_SHA256SUMS.txt)
python benchmarks/r10d_floor/comparison.py
```

Foram escritos **21 testes** que auditam handlists a partir da própria fonte, 169 classes BTN, preços, domínio, guardas, preservação dos 1.920 WHEN ancestrais, histórico, topologias e nuts em overbet. A [workflow 44860943038](https://github.com/pmartins87/Heuristic6max/actions/runs/44860943038) aprovou **573 execuções em 29 suítes**, sendo **561 testes deduplicados por suíte** (12 repetições do benchmark R10d); +21 testes sobre BLISO-2. Todos os testes são estáticos, sem OpenHoldem runtime.

## Próximos gates, sem mudança de estratégia anterior

**G1 ABERTO; G2-a HOLD; G6 PENDENTE**. Sem logs nem replays reais OpenHoldem, sem confirmação de `Set user`, ação final, reset, `PotSize/Calls`, `RaiseTo` ou fallback. VS_4BET/5BET ainda bloqueado; squeeze, defend after limp hero e multiway raised com 3+ adversários continuam pendentes. **0/14 capacidades do R10d integralmente VERIFIED; não usar em jogo real.**

Pai: `portability/blind_iso_v2/blind_iso_integrated_draft.oppl`. Novo integrado: `iso_defense_integrated_draft.oppl`.
