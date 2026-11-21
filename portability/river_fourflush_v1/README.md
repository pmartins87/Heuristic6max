# M08-RIVER4 — textura de quatro cartas de um naipe no river (DRAFT)

**Implementação estratégica real, não novo framework de auditoria.** A política é escrita em `river_policy.oppl`, combinada com todas as regras anteriores em `river_fourflush_integrated_draft.oppl`. Esta entrega **não** afirma GTO, EV positivo, lucro ou validação em OpenHoldem.

## Problema específico que a estratégia anterior tinha

No river SRP HU, a árvore ancestral `f$SRPHU` frequentemente considera `f$SRPStrongMade` suficiente para apostar meio pote ou dar call até 55% do pote, mesmo em uma mesa com **quatro cartas do mesmo naipe** e sem flush na mão do Hero. Isso inclui two pair, trips, set e straight, que continuam fortes em valor absoluto, mas se tornam **bluff-catchers** vulneráveis à posse de uma única carta daquele naipe pelo adversário.

O manual OpenPPL fornecido no projeto, em *Board Symbols*, define exatamente:
- `OneCardFlushPossible`: o board tem **4 ou 5 cartas do mesmo naipe**.
- `FlushOnBoard`: as **cinco** cartas do board têm o mesmo naipe.
- `HaveFlush` / `HaveNuts`: força efetiva do Hero (não tratar uma sequência como nut em 4-flush).

O módulo exige `OneCardFlushPossible AND NOT FlushOnBoard AND NOT HaveFlush AND NOT HaveNuts`. Ele age apenas em **four-flush exato**, não em toda mesa com três cartas iguais ou em flush compartilhado de cinco cartas.

## Novo comportamento OpenPPL no river

**Proveniência obrigatória:** `f$SRPHUOpen AND user_H6_RFIIntent` (RFI puro) **ou** `f$SRPHUCaller AND user_H6_VSOpenCallIntent` (cold-call contra abertura sem limper); exige ausência de flags conflitantes `RFI/VSOpenCall/3bet`. Esses helpers herdam `nplayersdealt=6`, `OpponentsOnFlop=1`, `OpponentsLeft=1`, `NOT StackUnknown`, nenhum all-in e contagens de raises anteriores. O controle é **específico de fonte**, não garantia de histórico real sem G1/G6.

| Cenário: exatamente quatro do mesmo naipe no board e Hero sem flush | Nova ação | Proteção intencional |
|---|---|---|
| `AmountToCall=0` | **Check** | Não apostar fino com bluff-catcher vulnerável |
| Aposta enfrentada, `f$SRPStrongMade`, preço até **20%** de `PotSize` | **Call** | Permitir bluffcatch muito barato com mão feita |
| Aposta enfrentada, `f$SRPTopGood`, preço até **10%** do pote | **Call** | Defesa mais restrita de top pair/overpair |
| Aposta maior ou sem a mão suficiente | **Fold** | Não pagar caro sem flush |

**Importante:** os números 20% e 10% são **heurísticas provisórias**, não thresholds de indiferença GTO ou estimativas de EV. A ordem `Call forte → Call top → Fold → Check` é deliberada; a ação em preço zero nunca produz Fold. **Flush ou nuts** são excluídos por guarda e permanecem governados pela árvore anterior. O módulo não contém fallback `WHEN Others` no callback river.

## Escopo e imutabilidade

- Pai congelado: `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`, SHA256 `27be1f161535c9bc07f019fd6e0609c7a3018bf6b2cc640b80a6042c5b7df02b`.
- Todas as **2.007 linhas WHEN** ancestrais aparecem na mesma ordem; nova saída tem **2.016 WHEN / 161 f$ / 192 listas / 121 Set user / 38 símbolos user_**.
- São quatro **decisões de ação novas**, mais cinco linhas `WHEN` dos dois helpers. Não altera ações de flop ou turn, antepassados, RFI/VS_OPEN/VS_3BET, ranges v0.6.1, potes ISO, 3bet, multijogador ou G2-a.
- O benchmark atual é atualizado para o novo OpenPPL integrado. A matriz mantém M08 como **PARTIAL**, demais critérios R10d intactos, **0/14 VERIFIED**.
- OH-G1G6-1 continua sendo o pacote de captura da **versão histórica ISODEF-1**; é proibido transferir a conclusão de replay para este novo integrado sem novo caso e inspeção.

## Verificação focada — não multiplicar testes

```bash
python -m unittest discover -s portability/river_fourflush_v1 -p 'test_*.py' -q
python portability/river_fourflush_v1/build_river.py
git diff --exit-code -- portability/river_fourflush_v1/river_fourflush_integrated_draft.oppl
(cd portability/river_fourflush_v1 && sha256sum -c RIVER4_SHA256SUMS.txt)
```

Os **7 testes focados** leem as quatro decisões efetivas de `river_policy.oppl`, verificando preço, origem estrita, exclusão de flush/nuts e preservação literal dos ancestrais; não constituem prova de OpenHoldem runtime. A CI enxuta mantém a regressão inteira apenas para PR pronta/main. **Próxima evolução estratégica proposta:** textura de straight/board pair e SPR com definição dos cenários que a árvore antiga trata mal, não acrescentar dezenas de regras por contagem.
