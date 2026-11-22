# F2-PILOT-01 — BTN vs BB SRP: primeiras decisões heurísticas baseadas em fontes

**Data:** 21/11/2026. **Escopo:** cash NLHE 6-max, BTN Hero RFI **2,5 BB**, BB call, SB fold, 100 BB efetivos de referência, flop HU, BB check, Hero IP. **RFI BTN alvo ~42% (faixa 41–44%), sem obrigação de acertar decimal**. As decisões abaixo são de estudo, não bot executável.

**Fontes:** [GTO Wizard — Mechanics of C-Bet Sizing](https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/); [GTO Wizard — Flop Heuristics: IP C-Betting in Cash Games](https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/); [ART/GTO — C-bet sizing](https://artgto.com/learn/why/c-bet-sizing-when-does-the-solver-bet-small-or-big/); [DeepCrusher_R10d](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt) apenas como referencial de roteamento/estado. Premissas e licenças em [../SOURCES.md](../SOURCES.md). **Não** se copiou árvore ou chart por combo.

## 1. Simplificação de produto validada como requisito, não como output de solver

- **Open raise padrão: 2,5 BB** em RFI do modelo inicial. Exceções de SB, profundidades diferentes, limpers/antes e decisões após um raise permanecem fora do primeiro domínio.
- **BTN first-in: 41–44% é tolerância de projeto; trabalhar com ~42%**. Não arredondar o mesmo número para LJ/HJ/CO/SB; cada posição tem range próprio.
- **Rake/cap do jogo real** só será necessário para calibração e release, **não bloqueia elaboração de uma heurística educativa inicial**. A referência ART/GTO usa 5% cap 3BB; não afirmar que esse é o rake-alvo.
- **Compressão inicial de sizing flop:** preferir duas opções implementáveis `BET_33` e `BET_75`, mais `CHECK`. Uma fonte de KJ7 permite 125%, mas adiar essa terceira opção é **trade-off de complexidade declarado**, não equivalência GTO.

## 2. Primeiros dois contratos estratégicos pontuais revisados

**SPOT-001 — QQ6 rainbow / trips com kicker alto:**
- Estado: flop **Q♥ Q♣ 6♦**, Hero **Q♠ J♠**, BB check; BTN IP RFI 2,5 BB, BB call, 100BB, sem ação flop anterior.
- **Decisão heurística revisada: BET_33% pot**. Razão: paired dry tende a gerar muitas small cbets; trips é valor forte, pode obter calls de 6x, pares, floats, e o sizing pequeno protege o restante da faixa. A referência profissional demonstra explicitamente QQ6r com cbet majoritariamente 33% e Qx como valor.
- **Contraditório:** slowplay/check com algumas trips pode ser legítimo; não afirmar frequência pure GTO nem estender bet automático a qualquer Qx, qualquer paired board, qualquer posição. Se a dinâmica de BB check-raise for anômala, política de resposta precisa de nó separado.
- Status: **STRATEGY_REVIEWED_HEURISTIC** neste *spot exato*, não OPPL_PARITY nem OH_VERIFIED.

**SPOT-002 — A73 rainbow / top pair com kicker fraco:**
- Estado: flop **A♠ 7♦ 3♣**, Hero **A♥ 5♥**, BB check; mesmos limites do spot acima.
- **Decisão heurística revisada: CHECK**. Razão: top pair fraco no A-high seco não exige proteção de overcards; check mantém mãos piores adversárias, evita bet/fold automático contra check-raise e preserva parte do range de check. O artigo profissional especificamente identifica weak Ax como classe que checka mais em A73r.
- **Contraditório:** apostar pouco por valor/proteção algumas vezes também pode ser válido; o check é simplificação heurística e depende de não haver draw ou exploit relevante.
- Status: **STRATEGY_REVIEWED_HEURISTIC** neste *spot exato*, não OPPL_PARITY nem OH_VERIFIED.

**Critério de aprovação aplicado:** há referência externa explícita da família exata de board, mão pertencente à classe discutida, ação simples e justificada, contraexemplo reconhecido, e nenhuma outra fonte presente a contradiz de forma impeditiva. A aprovação é **qualitativa por conveniência heurística**, não evidência de EV.

## 3. Matriz de expansão: somente DRAFT, sem ação final universal

| Família | Tendência profissional | Arquitetura candidata | Por que não promover já |
|---|---|---|---|
| Q♥Q♣6♦ paired dry | **C-bet pequena frequente** | Small `33%` com valor e parte dos bluffs; checks de proteção de range | BB possui Qx e 66, pode X/R; discriminar Qx, pares, overcards e air |
| K♥J♥7♦ two-tone | **Bet maior e mais polarizado** | `75%` com value forte e draws de alto potencial; check com parte de showdown | Fonte tem também `125%`; compressão pode alterar decisões por mão |
| Q♦J♦T♦ monotone connected | **Menos bets / menor sizing** | `CHECK` frequente; quando betar, `33%` para fração selecionada | Alto risco de confundir flush, straight e blockers; não bet/fold pela simples ausência de diamantes |
| A♠7♦3♣ ace-high dry | **Weak Ax frequentemente check** | Alguns value bets pequenos, muitos checks de Ax fraco/pares de showdown | A-high não significa cbet automática; BB X/R tem gama específica |

**Exemplos para posterior contraditório:** Q♥Q♣6♦ com A♠K♠ (A-high pode cbet/check); K♥J♥7♦ com Q♥T♥ (combo-draw) ou K♣J♣ (two pair); Q♦J♦T♦ com K♣9♣ (straight sem diamante) e A♦8♦ (flush forte com bloqueios); A♠7♦3♣ com A♦Q♦ (top pair bom). Não deduzir `RAISE` ou `FOLD` contra X/R sem contrato de resposta.

## 4. Sentinelas obrigatórias contra repetir erros da V1

- `FourFlush` / `NOT HaveFlush` / `NOT HaveNuts` jamais substituem a classificação exata de `HaveFullHouse`, `HaveQuads` ou `HaveStraightFlush`.
- `StrongMade` não é sinônimo de bluffcatcher frágil; range de aposta do oponente importa.
- `CHECK` grátis tem de ser permitido e executável, não cair em `Fold`.
- `NoMatch` em OH não é necessariamente safe: exige caminho explícito e replay.
- Remapeamento de aposta em pot fraction e `f$allin_on_betsize_balance_ratio` pode alterar ação final. Isolar testes e verificar sizing no runtime antes de promover.
- **O estado curto/deep e a origem 3-way do DeepCrusher não são o SRP cash 6-max 100 BB.**

## 5. Estado e próxima ação de engenharia

**F0:** PASS_CONCEPTUAL / DATASET_IMPORT_HOLD. **F1:** PASS_PILOT_CONTEXT para estes exemplos, com economia real mantida provisional. **F2:** OPEN com **2 decisões pontuais STRATEGY_REVIEWED_HEURISTIC**, demais DRAFT. **F3–F5:** BLOCKED. Nenhum `.oppl` V2 foi gerado, nenhum solver foi executado; não houve OH runtime.

**Próximo passo:** implementar isoladamente os dois spots revisados em OpenPPL *somente* quando símbolos e testes de precedência puderem expressar cartas/board/posição sem ambiguidade, e comparar ação/sizing offline. Expandir demais combos por fontes e estrutura, evitando repetir debates marginais de 41 vs 44% RFI.
