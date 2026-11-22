# F1-PILOT-01 — BTN vs BB SRP: contrato de evidência para c-bet no flop

**Criado:** 21/11/2026. **Estado atualizado ADR-046:** F1 PASS_PILOT_CONTEXT para BTN RFI 2,5 BB / ~42% (faixa aceita 41–44%); 2 decisões F2 pontuais revisadas em [CBET_F2_PILOT.md](BTN_BB_SRP_CBET_F2_PILOT.md); F2 global OPEN, sem OpenPPL novo. Subordinado a [../PLAN.md](../PLAN.md) e [../SOURCES.md](../SOURCES.md).

## 1. Qual o cenário que queremos cobrir?

Estudar **cash Texas Hold'em NLHE 6-max, 100BB efetivos, BTN (Hero) RFI para 2,5 BB; SB fold; BB paga; flop HU; BB check; Hero IP é o agressor pré-flop**. Nenhum ante, straddle, limper, 3bet, all-in, multiway, donk flop nem ação anterior nesta street.

- Blinds: SB 0,5 BB, BB 1 BB. Se a plataforma não aplica rake pré-flop, pote bruto ao flop **5,5 BB** (BTN 2,5 + BB 2,5 + SB 0,5). Stacks remanescentes dos dois jogadores = **97,5 BB**. Não aplicar uma soma de 6,5 ou contar a blind duas vezes.
- **Modelo econômico de comparação, não pressuposto da sala-alvo:** GTO Wizard lista 6max 100BB cash `General (NL50)` com 5% rake, **cap 4 BB** e BTN open 2,5 BB (fonte SRC-012). O exemplo de c-bet IP do blog usa uma solução `Simple` na qual BB **não pode dar donk**, e NÃO afirma que seja a mesma árvore/economia. Não misturar frequências entre versões.
- Referência alternativa ART/GTO: 6-max 100BB com **5% rake cap 3BB**, sizings de flop disponíveis **33% e 75%** no relatório BTN vs BB SRP. A página não expõe necessariamente o sizing pré-flop desse submodelo; **não** equiparar automaticamente ao cenário BTN 2,5 BB da nossa definição.
- **Rake e cap reais da plataforma final ainda não declarados.** O estudo tem escopo educacional/heurístico; antes de concluir F1 para implementação, registrar economia aplicável ou documentar tolerância de aproximação.

Chave de estado sugerida (não código): `cash6max/100bb/BTN_RFI_2p5/BB_CALL/SB_FOLD/flop/BTN_IP/BB_CHECK/rake_model_id/board_texture/hero_combo`. Quando houver `BB_DONK`, `SB_CALL`, `3BET`, `short_stack` ou histórico inconsistente, **fora do domínio**, nunca fallback estratégico silencioso.

## 2. Fontes externas verificadas e sua aplicação correta

**SRC-010 — [GTO Wizard, *Flop Heuristics: IP C-Betting in Cash Games*](https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/).** Analisa BTN vs BB SRP sob solução *Simple* com BB sem donk. Documenta que high-card boards tendem a favorecer o RFI; paired/disconnected permitem mais apostas; flops conectados e monotone incentivam mais checks ou sizing diferente. Atenção: nem todos os A-high são cbet compulsórias; muitos Ax marginais carecem de urgência de proteção. Trata-se de orientação condicional, não lista de ações por combo da nossa economia.

**SRC-011 — [GTO Wizard, *The Mechanics of C-Bet Sizing*](https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/).** Três **exemplos** BTN após BB check:
- `Q♥ Q♣ 6♦` (paired, rainbow, seco): apostas numerosas, predominantemente pequenas (~33% pote). Não generalizar que qualquer paired flop exige bet.
- `K♥ J♥ 7♦` (duas cartas do mesmo naipe, coordenado): as apostas dominantes no exemplo são 75% e 125%, com incentivo de proteção e polarização; **não** comprimir `125%` automaticamente para `33%`.
- `Q♦ J♦ T♦` (monotone muito conectado): o artigo descreve aproximadamente metade bet / metade check, predominando aposta pequena quando aposta. Não concluir `always check monotone`.

**SRC-013 — [ART/GTO, *C-bet sizing: when does the solver bet small or big?*](https://artgto.com/learn/why/c-bet-sizing-when-does-the-solver-bet-small-or-big/).** Evidência independente: 6max 100BB, 5% cap 3BB, apenas bet 33%/75% no flop; *paired* usa mais small e quase nada de big, boards conectados têm mais checks e mais bets grandes, monotone menos ação do que rainbow. Relatório é agregado/ponderado por board, não frequência de ação de uma mão isolada. Exemplos numéricos do site (não copiar tabela completa): paired 79,8% small / 7,4% big / 12,8% check; connected 46% small / 30,4% big / 23,6% check.

**SRC-014 — [GTO Wizard, *Why doesn't my solution match GTO Wizard?*](https://blog.gtowizard.com/why-doesnt-my-solution-match-gto-wizard/).** O próprio fornecedor relata **~53% vs ~64%** de frequência agregada de c-bet BTN vs BB quando o menor size disponível muda (~33% vs ~27%) e o range BB após 3bet pré-flop também muda. Demonstra por que não podemos importar frequências numéricas de árvores diferentes; **não** valida frequência ideal do nosso bot.

**SRC-015 — [GTO Wizard, *Poker Strategies: Tournaments vs. Cash Games*](https://blog.gtowizard.com/poker-strategies-tournaments-vs-cash-games/).** RFI BTN cash 6max, 100BB, 2,5BB, sem ante, aproximadamente 42% abre. O mesmo artigo compara 53% em MTT com ante, que não é transplantável.

**SRC-016 — [GTO Wizard, *Status and Info About Our Solutions*](https://blog.gtowizard.com/status-and-info-about-our-solutions/).** Lista configuração `General NL50`: 100BB, BTN 2,5BB, rake 5%, cap 4BB; outras bibliotecas (NL500 cap 0,6BB, Simple 2,5x) têm hipóteses diferentes.

**SRC-005 — [DeepCrusher_R10d](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt).** Inspecionado diretamente pelo blob SHA `9f9cba79cdb9dc4438895770cf61a450fb55d17c`:
- `f$flop_Raise_SRP_Initiative` diferencia IP/OOP, c-bet quando ninguém apostou, reações a donk/float/3bet, encaminhando a `f$move_flop_cbet`. **Reutilizar arquitetura histórica, não fórmula de apostas**.
- `f$move_flop_cbet` contém decisões por `f$game_HUSB`, `f$game_3wBTNvBB`, textura, força da mão, draws e memória `user_...`. No ramo `f$game_HUSB`, exemplo de check de TP depende de `f$EffectiveStack_BKP <= 16`; `f$game_3wBTNvBB` é **origem 3-handed**, não cash 6max. Cópia direta de thresholds e categorias produziria extrapolação indevida.
- `f$flop_DrawHeavy` e `f$flop_dry` mostram necessidade de verificar a **semântica real** dos predicados, não apenas nome textual. O arquivo R10d é candidato de hardening não promovido acima do R10c segundo docs/STATUS.md do projeto DeepCrusher.

## 3. Contrato estratégico candidato por FAMÍLIA — não é uma regra!

| Família / board piloto | Referência profissional | Direção estratégica plausível **não aprovada** | Contraprova e guardas antes de F2 |
|---|---|---|---|
| **PAIRED-DRY** Q♥Q♣6♦ | SRC-010/011/013 | Priorizar análise de **aposta pequena com frequência relativamente alta**; alguns checks de controle/mix | BB pode possuir Qx/66, mãos do BTN de showdown valor podem preferir check; não impor bet para qualquer par/air |
| **WET-TWOTONE** K♥J♥7♦ | SRC-010/011/013 | Apostas mais **polarizadas**, check com parte da faixa média; considerar **75% e 125%** conforme modelo, draw, nuts e blockers | Se remover 125% da árvore, documentar mudança; draws nem sempre cbet; posição, BB check-raise e turn impactam |
| **MONOTONE-CONNECTED** Q♦J♦T♦ | SRC-010/011/013 | **Mais checks** e bet pequeno em parte dos combos, sem regra de "sempre check"/"fold sem flush" | Made straight, flush, set e blockers se comportam diferentemente; ver contribuição da hole card; não transportar frequências de monotone seco |
| **ACE-HIGH-DRY** A♠7♦2♣ | SRC-010 | RFI tem vantagem de overcards mas alguns top-pairs Ax marginais podem preferir check por falta de proteção urgente | Não presumir 100% cbet só por A high; comparar com flop K-high e draws possíveis |

**Famílias estratégicas por combo a revisar em F2:** nuts/value muito forte, value forte mas vulnerável, top/middle/underpair, draws de flush/straight/combo/backdoor, overcards, air com/sem blockers, mãos que ganham equity contra vilão que aposta/call, e mãos que preferem realizar equity com check. Entender quem continua versus os sizings e reavaliar no turn.

**Ações candidatas para o estudo, NÃO sizing aprovado:** `CHECK`, `BET_33`, `BET_75` e `BET_125` (esta última porque a fonte específica usa overbet em um dos flops). Não definir nenhuma probabilidade/condição final antes da aprovação F2. Não equiparar bet size a aumento no OpenPPL sem verificar semântica real.

## 4. Avaliação contraditória e precedência anti-erro

1. "Quanto maior/mais forte minha mão, maior minha c-bet" é falso como regra geral: dry paired nut pode beneficiar-se de small com todo o range; wet/polarizado pode usar bet grande e checking range.
2. "A-high = bet sempre" contrariado pelo SRC-010; top pair marginal pode desejar check.
3. "Monotone = check sempre" contradiz SRC-011/013; alguns bets e blefes permanecem.
4. "R10d usa TP+ bet ~40%, logo cash 100BB deve apostar 40%" **rejeitado**. Tipo de jogo, ranges, rake, SPR e contexto diferem.
5. "Se código passar no teste sintático está estrategicamente aprovado" **rejeitado**: teste deve comparar ação contra contrato de estratégia apoiado em fonte externa, não reproduzir uma regra autorreferente.
6. Separar **qualidade do nó** (F1) de **seleção de ação por combo** (F2) e de execução OpenPPL/OH (F3/F4).

**Checks sintéticos futuros (apenas contrato):** BTN preflop RFI 2.5 com BB call e SB fold, 5.5bb pot, 97.5bb stack; comparar Q♥Q♣6♦ / K♥J♥7♦ / Q♦J♦T♦ / A♠7♦2♣, alternando Hero nut made/medium/draw/air. Para cada caso registrar ação e explicação que considere ranges/BB check-raise, e os eventos permitidos na árvore.

## 5. Gate e critérios de parada (histórico anterior à escolha pragmática ADR-046)

- **F0 conceptual PASS restrito:** há fontes profissionais suficientes e compatíveis *em princípios gerais* para prosseguir ao estudo heurístico; **não há licença verificada para importar tabelas/árvores de GTO Wizard, ART/GTO ou Upswing como datasets em código**.
- **F1 OPEN:** cenário e primeiros quatro boards definidos; pendente economia-alvo operativa, premissas pré-flop exatas por combo, semântica dos sizings de OH e escolha explícita da árvore comprimida para primeira política.
- **F2 BLOCKED:** nenhuma regra por combo ou porcentagem aprovada; nenhuma cbet publicada como política V2.
- **F3/F4/F5 BLOCKED:** nenhum OpenPPL novo, replay OH, nem comparação estratégica validada ao R10d.
- **Stop:** se os inputs reais não forem observáveis (BB check/histórico, stack, origem SRP, board), rejeitar automação em vez de produzir fallback silencioso. Se chart/solução não for reutilizável, extrair *princípio qualitativo original* e não reproduzir banco de dados protegido.

**Próximo passo concreto F1:** fixar ou manter explicitamente provisório o regime de rake/cap do produto-alvo; registrar ancestral RFI/BB-call compatível e política de compressão de sizing em `v2/` antes da revisão F2 dos quatro boards. Sem executar solver.


## 6. ADR-046 — escopo aceito pelo usuário e novo estado de gate
- **RFI padrão do piloto = 2,5 BB; BTN ~42% de abertura com tolerância 41%–44%**. Não investigar diferenças percentuais dentro desta banda sem nova evidência que altere decisões materialmente. Outras posições não recebem a mesma taxa de RFI.
- Modelo de 100 BB e BTN vs BB SRP mantém os requisitos de **estado real** (posição, BB check, limpers/3bets ausentes, cartas e sizing); rake exato é **premissa provisória de calibração**, não impedimento para protótipo educativo.
- **F1 PASS_PILOT_CONTEXT** para os quatro boards descritos; exceções de rake, múltiplos jogadores, stack curto e mudanças de linha continuam fora do domínio.
- **F2 OPEN**: [dois spots pontuais revisados](BTN_BB_SRP_CBET_F2_PILOT.md), vários comportamentos de classe DRAFT. Não generalizar um spot aprovado a todos os combos.
- F3–F5 BLOCKED; próximo passo **não** é mais comparar 40,9% versus 43,1%, mas traduzir os dois primeiros contratos estratégicos com semântica OpenPPL inspecionada e testes offline.
