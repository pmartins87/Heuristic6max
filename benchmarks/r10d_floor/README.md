# R10d como PISO OBRIGATÓRIO de abrangência funcional (ADR-028)

**Não é um comparativo científico de EV. É um gate de engenharia e estratégia.** O usuário determinou que a versão final do Heuristic6max precisa ser, no mínimo, **mais completa que o DeepCrusher_R10d**, sem importar automaticamente suas decisões. **O requisito ainda NÃO foi atendido.**

## Fonte medida diretamente

Arquivo GitHub exato: [`pmartins87/DeepCrusher/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt`](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt). Blob Git `9f9cba79cdb9dc4438895770cf61a450fb55d17c`, SHA256 declarado no repositório DeepCrusher: `1b198b70...f46f` (valor completo em `R10D_REFERENCE.json`). São 1.325.138 bytes, 20.788 linhas, 725 funções `f$`, 545 handlists, 6.021 instruções `WHEN`, 1.561 instruções `Set user` e 561 variáveis `user_` distintas. O relatório R10d cita **1.271 cabeçalhos** contando a seção adicional `##notes##`; os 1.270 são exatamente 725+545.

Isso caracteriza um **gap significativo**, mas **não implica exigir mais de 6.021 WHEN**: linguagem mais concisa, reutilização e cobertura verdadeira podem ser superiores com menos linhas. Uma árvore imaginária de 484 históricos não supera centenas de linhas efetivamente executáveis.

O R10d é um **candidato de hardening**; o DeepCrusher documenta R10c como baseline operacional, que não deve ser confundida com certificação runtime do R10d.

## Gate de aceitação e plano por prioridades

`CAPABILITY_MATRIX.csv` rastreia **14 famílias obrigatórias**. Não usar percentual de linhas de código como critério de conclusão. O objetivo de produto inclui: pré-flop integral 6-max (4bet, 5bet, squeeze, blinds, limp/iso e stacks distintos); SRP, 3bet, 4bet, multiway 3way e **4+ jogadores**; histórico cronológico e eventos realizados; classificadores de board/runout, nut advantage e blockers; sizing, SPR e compromisso/all-ins; perfil do oponente com fallback sem PT4; ação final legal em OpenHoldem e robustez estratégica.

Gates recomendados, pela ordem de redução de erros graves:

1. **A — Identificar pote e histórico realmente observado** (RFI versus 3bet/4bet, limper/iso, 2–6 players, flags persistentes). Resolver ambiguidades; fora de domínio, não inventar decisões.
2. **B — Completar famílias com ação real:** SRP HU e potes 3bet HU (novo v1), depois limped/iso e multiway, 4bet/5bet e short stack. Subdividir por posições, força/range, textura/runout, SPR, preço e plano street seguinte. Não contar classes sem ação.
3. **C — Adaptação e avaliação prática:** rake/cap, sizings e adversário, perfil amostral, showdown/feedback e estabilidade. Testes funcionais reproduzíveis; não exigir solver nem prova matemática GTO.
4. **D — Gates de execução:** compilar/rodar OpenHoldem real offline, verificar histórico, reset, ação final, fallback, legalidade e rollback. Não promover enquanto houver lacuna essencial.

**Critério de parada de desenvolvimento:** se as lacunas de observabilidade se mostrarem intransponíveis na versão OH-alvo, corrigir arquitetura/adaptador ou reconsiderar tecnicamente a plataforma antes de escrever milhares de regras sem efeito. **Critério de não entrega:** a ausência de qualquer família M01–M14 verificada impede dizer que a versão final superou o R10d.

A abrangência deve ser **dominância funcional**: cobrir no mínimo as famílias efetivamente documentadas do R10d, com amplitude adicional (por exemplo, multiway com 4–6 jogadores), e mostrar decisões significativas/reprodutíveis em estados alcançáveis. Não importar a estratégia do DeepCrusher: ADR-006 permanece válida. Não alterar ranges pré-flop v0.6.1 para aumentar métrica de completude.

## Auditor automático (não é juiz de GTO)

```sh
python -m unittest discover -s benchmarks/r10d_floor -p 'test_*.py' -q
python benchmarks/r10d_floor/comparison.py
git diff --exit-code -- benchmarks/r10d_floor/CURRENT_GAP_REPORT.json
# intencionalmente NÃO passa até o piso ser superado e aprovado:
python benchmarks/r10d_floor/comparison.py --release-check
```

Um SHA, um rótulo `VERIFIED` ou uma contagem grande **não demonstram** execução real. `PROMOTION_GATE.json` permanece false até apresentação de evidência de OpenHoldem e aceitação de cobertura/qualidade. A CI somente exige **honestidade e regressão**, não marca como pronto. O protocolo não substitui a estratégia.

O R10d está no GitHub do outro projeto; **não duplicar** 1,3 MB de código-fonte alheio nem citar R10d como tendo validação runtime que seus documentos não afirmam.

## Atualização de abrangência — Multiway-v2 + LIMP-BB-v1 (20/11/2026)

- Fonte integrada ativa agora em [`portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl`](../../portability/limped_bb_v1/preflop_multiway_limp_bb_draft.oppl): pré-flop RFI/VS_OPEN/VS_3BET preservado; pós-flop SRP HU/HIST-v3, 3bet HU, 3way, e os dois novos módulos.
- [`portability/multiway_v2/`](../../portability/multiway_v2/) acrescenta **40 decisões 4–6-way** SRP sem desistências posteriores e **34 para multiway→HU** (inicialmente 3–6 jogadores). Ainda faltam topologias intermediárias.
- [`portability/limped_bb_v1/`](../../portability/limped_bb_v1/) acrescenta **33 decisões pós-flop** e **duas opções pré-flop de check do BB contra um limper**; limp/iso geral continua pendente.
- 25 + 17 = **42 novos testes**, total acumulado esperado **434**. Comparação mede o último artefato integrado, sem apagar histórico ou se apropriar das decisões DeepCrusher.
- Gate NÃO ALTERADO: 14 capacidades ainda têm lacunas e 0 atingiram evidência completa. `PROMOTION_GATE.json` permanece integralmente `false`. Não descrever o bot como superior ao R10d neste estágio.
