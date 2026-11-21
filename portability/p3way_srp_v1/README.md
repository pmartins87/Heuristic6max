# Heuristic6max — 3-way SRP flop/turn/river v1 DRAFT

Esta entrega inicia **uma família multiway de verdade**, em vez de classificar 484 caminhos apenas no papel. São **31 novas regras OpenPPL de ação** (13 flop + 10 turn + 8 river), e quatro helpers que distinguem o Hero que abriu primeiro de quem pagou abertura adversária pré-flop.

## Proveniência e integração

- `preflop_coldcall_intent.oppl`: 33 comandos `Set user_H6_VSOpenCallIntent`, gerados das 33 regras originais `VS_OPEN Call FORCE` — sem mudar nenhuma ação pré-flop de origem. O histórico de CALL deve também ser confirmado por `BotCalledBeforeFlop` no estado posterior.
- `threeway_srp_postflop.oppl`: a fonte **OpenPPL** das 31 ações, com guardas para **exatamente 2 adversários no flop e ainda 2 ativos**, sem all-in/StackUnknown e posições/contagens de raises coerentes. Não usar um single-raised pot com 3way como se fosse heads-up.
- `preflop_srp_3bet_3way_draft.oppl`: arquivo integrado a partir de `p3bet_hu_v1`, com novas 33 marcações de intenção e ações 3way prioritárias, mas mutuamente excludentes das 3bet HU e SRP HU. Nenhum arquivo histórico foi alterado.
- `threeway_interpreter.py`: intérprete restrito da **mesma fonte** OpenPPL para teste; `test_threeway.py`: 16 testes novos. `build_threeway.py`: gerador offline reprodutível.

As heurísticas conservadoras consideram força, pot odds, draw, posição, textura e mistura estável por `randomhand`. **Não há alegação de GTO exata**, nem evidência de qualidade comparativa versus DeepCrusher R10d.

## Limitações essenciais

Potes com quatro ou mais jogadores ativos, flop 3way que se tornou HU, multiway 3bet/4bet, limped/iso, squeeze, potes em que o Hero é o BB que apenas deu check pré-flop e todos os casos all-in **não são cobertos**. Somente as linhas com origem RFI ou CALL VS_OPEN previamente codificada podem entrar neste módulo. Isso é deliberado para evitar classificar caminhos sem histórico e fingir completude.

`Set user` é uma **intenção**, não um registro irrefutável de ação final. A confirmação nativa e a avaliação na instalação OpenHoldem ainda são necessárias. Um retorno `None` do interpretador para domínios desconhecidos NÃO assegura que o OpenHoldem deixará de usar seu `default.bot`. Portanto, **não executar o draft em mesa real**.

## Reproduzir

```sh
python -m unittest discover -s portability/p3way_srp_v1 -p 'test_*.py' -q
python portability/p3way_srp_v1/build_threeway.py
git diff --exit-code -- portability/p3way_srp_v1/preflop_coldcall_intent.oppl portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl
(cd portability/p3way_srp_v1 && sha256sum -c P3WAY_SRP_SHA256SUMS.txt)
```

**Requisito de produto final permanece:** superioridade funcional ao DeepCrusher_R10d em todas as 14 famílias do [benchmark](../../benchmarks/r10d_floor/README.md). Nesta entrega, M05 passa de MISSING para PARTIAL, não VERIFIED. O primeiro payoff real de engenharia é cobrir 3way com decisões e guardas; o próximo é ampliar cronologia, 4–6 jogadores, outros tipos de pote, posições, SPR e sizings.
