# Multiway-v2 — SRP de 4 a 6 jogadores e transições multiway → heads-up

**Heuristic6max, 20/11/2026 — DRAFT, sem execução no OpenHoldem real.** Objetivo é um bot completo, no mínimo mais abrangente que o DeepCrusher_R10d. Esta etapa aumenta cobertura efetiva, mas não atinge o piso final. Não é estudo científico nem solver; é estratégia heurística OpenPPL em construção.

## Implementação

- `crowded_srp_postflop.oppl`: **40 regras de ação** (16 flop, 13 turn, 11 river) para potes originalmente de **4, 5 ou 6 jogadores** (3, 4 ou 5 oponentes desde o flop), sem saídas de jogadores após o flop. Distingue PFR e caller pré-flop. Quanto mais adversários, mais conservadores os calls sem nuts, os preços permitidos para draws e as apostas marginais. Não faz c-bet de air em potes muito disputados.
- `transition_to_hu_postflop.oppl`: **34 regras** (13 flop, 12 turn, 9 river) para potes que começaram **3-way até 6-way** (`OpponentsOnFlop = 2..5`) e agora têm **somente um adversário** (`OpponentsLeft=1`). Não confundir com um pote heads-up desde o flop. Regras mais seletivas quando o pote começou 4-way ou mais.
- `preflop_multiway_v2_draft.oppl`: arquivo integrado ao pré-flop e pós-flop anteriores, gerado por `build_multiway_v2.py`. **Nenhum `WHEN` anterior foi apagado ou reordenado e o trecho pré-flop permaneceu byte-idêntico.** Novos helpers e decisões são inseridos antes dos módulos anteriores, com domínios mutuamente exclusivos.
- `multiway_interpreter.py` interpreta somente as regras dos dois arquivos OpenPPL, sem uma segunda política de pôquer. `test_multiway_v2.py` traz **25 testes** com domínios, forças, preços, nuts, origem, estabilidade de `randomhand`, limites e preservação dos ancestrais.
- `MULTIWAY_V2_TOPOLOGY.csv`: inventário de **40 combinações estruturais** de oponentes no flop, oponentes restantes e papel pré-flop. O novo módulo admite 6 configurações de 4–6-way sem folds + 8 variantes de transição HU (contagens incluem dois papéis pré-flop). As outras 26 configurações **não são falsamente declaradas cobertas pelo novo módulo** (algumas são de competência dos módulos anteriores).

## Condições e limitações obrigatórias

O domínio exige 6 jogadores que receberam cartas, nenhum adversário all-in, stack conhecido, marcadores OpenPPL de RFI ou VS_OPEN Call e confirmação nativa do que o Hero fez antes do flop. A ausência de `user_H6_RFIIntent` / `user_H6_VSOpenCallIntent`, ou qualquer 3-bet contraditória, bloqueia o novo módulo.

A primeira família só cobre configurações com **nenhum fold depois do começo do flop**: 3→3, 4→4, 5→5 adversários. A segunda cobre 2→1, 3→1, 4→1, 5→1. **Ainda faltam 4→3, 5→4, 5→3 e outros cenários intermediários**, múltiplos raises, potes multiway 3-bet, limp/iso, range posterior de vilão, SPR calibrado e ação final ilegal. Isso NÃO representa todas as trajetórias históricas possíveis desses potes.

O valor `OpponentsOnFlop` e `OpponentsLeft` vem da biblioteca OpenPPL, mas os símbolos e a identificação da origem ainda precisam ser testados com o OpenHoldem instalado. Um `None` no interpretador estático NÃO garante bloqueio seguro no OpenHoldem (`default.bot`/fallback). Não operar com dinheiro real.

## Reproduzir da raiz

```sh
python -m unittest discover -s portability/multiway_v2 -p 'test_*.py' -q
python portability/multiway_v2/build_multiway_v2.py
git diff --exit-code -- portability/multiway_v2/preflop_multiway_v2_draft.oppl portability/multiway_v2/MULTIWAY_V2_TOPOLOGY.csv
(cd portability/multiway_v2 && sha256sum -c MULTIWAY_V2_SHA256SUMS.txt)
```

O próximo ganho será cobrir quedas intermediárias do número de jogadores com histórico confiável e depois ligar diferentes boards/runouts, sizings e SPR aos nós. Não adicionar mil regras indiferenciadas para mascarar lacunas.
