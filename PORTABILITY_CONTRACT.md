# Heuristic6max — contrato de portabilidade obrigatória OpenPPL (ADR-016)

**2026-11-20 · Gate PORT-0 iniciado; NÃO operacional.** Contrato transversal ao roadmap; preserva G0/G1/G2 e não inicia antecipadamente a integração G6.

## Objetivo e recomendação de arquitetura

Não manter duas implementações independentes de uma decisão. **Cada regra que decide ação no runtime deve nascer em um subconjunto explícito da linguagem OpenPPL, com equivalência de semântica verificável.** O Python que simula essas regras lê o MESMO texto OpenPPL; não reimplementa a estratégia com estruturas arbitrárias.

A exigência de equivalência **linha a linha literal Python ⇔ OpenPPL** não é implementável como promessa universal: a sintaxe é diferente, Python tem estruturas que OpenPPL não oferece, e OpenHoldem adiciona semânticas próprias de runtime. A garantia útil é: **cada ramo de decisão tem uma origem OpenPPL audível e a mesma regra é interpretada em Python com testes de paridade**. Sempre que a paridade não puder ser demonstrada, o ramo fica sem promoção para execução.

Não limitar bibliotecas de **auditoria, Monte Carlo, importação de charts, testes, exportação e reconstrução de histórico offline**. Elas não são lógica de decisão no runtime e não precisam virar OpenPPL. Limitar **apenas o núcleo de regras e seus predicados/ações**.

## Extraído do manual local efetivamente consultado

Fonte: anexo `OpenHoldem e OPPL Manuais e Library.zip` → `OpenPPL Manual.pdf` e `OpenPPL_Library_Integrated.txt` (documentação de aproximadamente 2015; **versão executável do OpenHoldem alvo não verificada**). O manual suporta:
- Seções `##f$preflop##`, `##f$flop##` etc., regras `WHEN condição ação FORCE`, `RETURN`, `RaiseTo`, `RaiseBy`, `Call`, `Check`, `Fold`.
- Execução de condições **de cima para baixo**: a primeira correspondente prevalece.
- Um único nível de condições `WHEN` abertas; múltiplos níveis de aninhamento **não** são suportados.
- `hand$AA`, `hand$AQSuited` e outras expressões de mão, handlists `##list...##` e funções `f$...`.
- `Random` inteiro em [0,99] versus `random` OH-script real em [0,1); não confundir.
- `Set user...` e memória OH `me_st_...` têm limitações de persistência/reinicialização. O manual alerta que símbolos baseados em histórico e scraping podem ficar indefinidos ou inconsistentes.
- O OpenPPL pode adaptar uma aposta ilegal ou usar uma **ação substituta**, inclusive Call/Check/Fold. Isso **não** é o mesmo que a falha explícita `None` prevista pelo nosso contrato Python.

## Regras mandatórias a partir de agora

1. **Fonte de verdade da lógica executável:** texto OpenPPL restrito, versionado, ou representação declarativa que gere OpenPPL e simulador a partir da MESMA fonte; nunca dois algoritmos com decisões independentes.
2. **White-list inicial:** `WHEN`, `AND`, `=`, `InButton`, `Raises`, `Calls`, `hand$AA`/`hand$KK`, `RaiseTo 2.5 FORCE`, somente em **prova demonstrativa BTN RFI**. Novos símbolos/operações requerem evidência de suporte real, adaptação do intérprete e teste de paridade.
3. **Bloqueados no runtime sem ponte de paridade:** `hashlib/sha256` como sorteio estável, `dict`, loops, classes/Enum, algoritmos de equidade, estado privado não observável, `source_quality=HIGH` sem predicado equivalente em OH, 4bet sem controle de legalidade equivalente.
4. **Misturas:** sem `Random` ingênuo em múltiplos ciclos de leitura. A seleção de ação deve permanecer estável no mesmo nó/mão. Não promover misturas antes de mecanismo de memória e resete verificáveis no OpenHoldem alvo.
5. **Fallback:** Python `None` NÃO equivale a `WHEN Others Fold/Check` e o OpenHoldem pode aplicar ações de backup. Sem mapeamento de falha explícita, **bloquear a promoção operacional** do ramo.
6. **Escopo mínimo do gate de paridade:** mesmo predicado/ação/prioridade, sizing **RaiseTo vs RaiseBy**, unidades (BB), guarda de posição/stacks/ação anterior, legalidade, estado do scraping, histórico estável, repetidas avaliações e resultado final do OpenHoldem (não só parser estático).
7. **CI:** para cada novo módulo de decisões, exigir regras OPPL, intérprete de testes do subconjunto, casos positivos/negativos, reprovação de construções não mapeadas. Arquivos anteriores permanecem históricos e **não são declarados portáveis retroativamente**.
8. **Gate real de G6:** testes do comportamento no OpenHoldem de versão especificada, com snapshots e replays de TESTE sem apostas, comparação da ação final, e fallback/rollback. O piloto atual **não foi compilado nem executado no OpenHoldem**.

## Prova implementada neste checkpoint

`portability/portable_rfi_probe.oppl` possui **duas regras nativas de OpenPPL** para BTN RFI puro AA/KK, 2,5 BB, só como prova de conceito. `portability/oppl_probe.py` é apenas intérprete de testes desse subconjunto. `portability/test_oppl_probe.py` cobre **3.042 estados de mão/posição/contadores** e recusa funcionalidades não permitidas. Falta guarda real de mesa 6-max, stack efetivo, scrape, validação de histórico, ação final, e a semântica de **não correspondência** não é idêntica ao OpenHoldem. **Não carregar como perfil executável.**

## Critérios condicionais

- **PORT-0** (contrato e piloto estático): aprovar somente após CI; não equivale a bot.
- **PORT-1** (1 nó completo sem mix): somente após identificação dos símbolos OH e paridade de ações em casos normais/limite.
- **PORT-2** (misturas e histórico): somente com persistência aleatória comprovada e estado confiável.
- **PORT-3 / G6**: OpenHoldem real, replays, legalidade, fail-closed, regressão paritária; bloqueado até G2 estratégico e G1 exigirem avanço.

A cada nova implementação estratégica, consultar este contrato e atualizar `DECISIONS.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `HANDOFF.md`, `README.md`, `CHANGELOG.md`, `RELEASE_MANIFEST.md`. **Não modificar os ranges RFI/VS_OPEN/VS_3BET neste checkpoint.**

## PORT-1 parcial — evidência de compatibilidade estática (ADR-017, 20/11/2026)
- [portability/port1/README.md](portability/port1/README.md) apresenta o subconjunto LJ RFI com 43 pure raises, 125 pure folds, KJo 40% raise não implementado; 15 testes e fonte única OpenPPL.
- Guardas sob verificação: IsPreflop, nplayersdealt=6, InUTG, Raises, Calls, StillToAct, PotSize, AmountToCall, StackUnknown, StackSize, MinOpponentStackSize e MaxOpponentStackSize. A documentação fornecida descreve esses símbolos, mas seus valores no OH-alvo não foram verificados.
- **PORT-1 continua ABERTO.** Interpretador Python None em regra ausente não assegura fallback seguro no OpenHoldem; ainda exige mistura KJo estável 40/60, OH real, legalidade, sizing, snapshots e replays de teste.
