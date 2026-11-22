# DeepPoker Strategy V2 — Plano Vivo (evidência profissional, sem solver próprio)

**Decisão atualizada:** 21/11/2026 — ADR-044. **Estado:** V2 metodologicamente redefinida; nenhuma política estratégica V2 aprovada nem executada. **Fonte única de verdade** do projeto V2: este arquivo. Evidências/proveniência do F0 em [SOURCES.md](SOURCES.md). GitHub/engenharia V1 e DeepCrusher_R10d são preservados; a V1, inclusive as 2.016 instruções WHEN da última integração, é `LEGACY_UNVALIDATED` para qualidade estratégica.

## 1. Objetivo e correção da metodologia

Produzir um **bot heurístico de cash NLHE 6-max**, fundamentado em **charts e soluções pré-calculadas publicadas, teoria profissional documentada, evidência estratégica independente e revisão de lógica do pôquer**, com execução OpenPPL/OpenHoldem **somente após** revisões e validação offline. Objetivo: comportamento **inspirado no GTO / próximo dos princípios GTO**, sem declarar equivalência a GTO nem desvio quantitativo conhecido enquanto não houver dados comparáveis.

**Decisão explícita do usuário:** NÃO calcular novas soluções com solver, NÃO instalar/rodar GTOpen ou TexasSolver como gate do projeto, NÃO exigir EV calculado por solver nem simulações próprias de árvores para aprovar cada heurística. Soluções profissionais já computadas e publicamente acessíveis são **referências para estudo**, desde que os direitos de uso permitam. Lógica do pôquer, pot odds e métricas operacionais básicas continuam necessárias; abandonar o solver **não** significa proibir matemática elementar.

**Não confundir:** passagem de 611 testes/CI da V1 comprovou conformidade com requisitos errados em parte do código, e não qualidade das decisões. A regra M08-RIVER4 poderia foldar full house por ter atravessado uma condição `four-flush` com limiar genérico. Isso é uma falha de especificação/precedência e força de mão; não pode voltar a ser aprovado por testes autorreferenciais.

## 2. Hierarquia das fontes e admissibilidade

1. **Regras objetivas de Texas Hold'em e semântica do OpenHoldem**: hierarquia de mãos, contribuição das hole cards, nuts/second nuts, combinação possível com blockers, ações legais, símbolos e história.
2. **Estratégia profissional publicada de alta qualidade**: charts pré-flop 6-max, artigos didáticos com exemplos situacionais e, quando permitido, soluções GTO pré-calculadas. Cada afirmação deve indicar URL/título, autoria/editor, data de consulta, posição, jogo, efetivo, rake quando indicado, sizings e diferença entre contexto da publicação e contexto do bot.
3. **DeepCrusher_R10d e sua documentação-fonte**: biblioteca de conceitos/caminhos, máquinas de estado, c-bet em SRP, linhas turn/river, experiência de desenvolvimento e piso obrigatório de abrangência. **Não é gabarito GTO**; não copiar decisões/limiares sem revisão profissional independente. Referência congelada em `benchmarks/r10d_floor/`.
4. **Heurística nova da equipe**: permitida apenas como aproximação/reconciliação documentada, com incerteza e alternativas explícitas. Nunca alegar que veio de solver se não veio.

Fontes iniciais para triagem e estudo (não são licença de incorporação integral):
- Upswing Poker, 6-max preflop charts: https://upswingpoker.com/charts/ ; URL fornece aberturas por posição e sizings, mas o alcance, atualização e uso permitido precisam ser conferidos.
- GTO Wizard, *The Mechanics of C-Bet Sizing*: https://blog.gtowizard.com/the-mechanics-of-c-bet-sizing/ ; mostra que posição, vantagem de range/nuts, textura e fold equity mudam frequência/sizing.
- GTO Wizard, *Maximizing Value on Monotone Flops*: https://blog.gtowizard.com/maximizing-value-on-monotone-flops/ ; exemplos de four-flush river, checks, apostas de valor e blefes, com escopo específico, não generalizável cegamente.
- GTO Wizard, *Do Multiple Sizes Matter?*: https://blog.gtowizard.com/do-multiple-sizes-matter/ ; fundamenta **simplificação controlada** de sizings, com maior risco de erro no river.
- Termos GTO Wizard: https://gtowizard.com/terms/ ; **não utilizar comercialmente nem redistribuir árvores/ranges/charts obtidos do serviço sem permissão explícita**. Referenciar conceitos publicados não concede direito de copiar uma base proprietária.
- DeepCrusher_R10d exato: https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt

Usar duas fontes independentes **quando existirem**, sem criar exigência mecânica que impeça revisão de um fato elementar; registrar discrepâncias e suspender uma decisão controversa se não houver base suficiente. **“Está público” não significa “domínio público”.**

## 3. Princípios estratégicos que a arquitetura deve manter

- Antes de avaliar `board texture`, classificar **a melhor mão de cinco cartas com as sete disponíveis**, força relativa/nuts, origem de sua força (hole cards vs board) e combinações adversárias superiores legalmente possíveis. Uma quarta carta do naipe **não rebaixa um full house para flush**. Full house supera flush comum; pode perder para full house maior, quads ou straight flush.
- **Proibição:** uma regra de textura genérica ou limiar de bet-size não pode foldar automaticamente uma mão extremamente forte sem revisão explícita da composição de ranges e da linha do vilão. Não impor o inverso `never fold full house` universal: há runouts/cenários raros nos quais uma mão superior é possível.
- Toda política precisa distinguir **range vs range**, posição/IP-OOP, origem RFI/call/3bet/limp, número de jogadores por street, mudanças de iniciativa, ações ordenadas, `SPR`, profundidade efetiva, rake, board/runout, nut advantage, preço, blockers e sizing.
- **C-bet SRP** pode reutilizar princípios de jogabilidade de 100BB em profundidades próximas e ser base reaproveitável no DeepCrusher; **não** assumir que o stack deixa de importar. SPR, stacks curtos e potes 3bet mudam opções de sizing, compromisso e risco. Portar o **princípio**, revalidar exceções dependentes de stack.
- Estratégia agressiva precisa incluir check, value, proteção, delayed c-bet, semi-bluffs e **blefes** nos contextos apropriados. `Sempre check com ar` ou `nunca blefar river` não equivale a GTO.
- Uma mesma categoria da mão (“top pair”, “flush”) não determina ação sem contexto. Sem evidência suficiente, a política permanece DRAFT; sem observabilidade/runtime seguro, não operar.

## 4. Fluxo de trabalho obrigatório

```text
FONTE profissional publicada / solução pública existente / lógica objetiva
    -> QUALIFICAÇÃO DA FONTE, DIREITOS e PREMISSAS do spot
    -> REVISÃO ESTRATÉGICA (range, história, força, blockers, posição, SPR)
    -> ESPECIFICAÇÃO DE DECISÃO E EXCEÇÕES em cenário alcançável
    -> REVISÃO CONTRADITÓRIA por fontes alternativas e DeepCrusher
    -> IMPLEMENTAÇÃO OpenPPL (fonte da ação)
    -> TESTES focados de precedência, mãos fortes, ações legais, transições
    -> REPLAY OFFLINE no OpenHoldem, log de decisão/tomada/fallback
    -> COBERTURA R10d + avaliação de robustez; promover só após gates
```

É proibido gerar milhares de decisões arbitrárias e usar a CI para declará-las boas. Não exigir rodar solver próprio, calcular EV por combo ou Monte Carlo sem pergunta realmente indispensável. Testes **verificam implementação**, fontes/contraditório **fundamentam estratégia**. Revisões qualitativas não quantificam a distância para GTO nem asseguram lucro.

## 5. Gates revisados (F0–F5)

| Gate | Evidência mínima / aprovação | Estado atual | Se falhar |
|---|---|---|---|
| **F0 Fontes e viabilidade heurística** | Catálogo inicial de referências profissionais acessíveis, pressupostos/jogo, direitos de uso e critérios de admissibilidade. Comparar com escopo R10d. **Não executar solver.** | **OPEN** | Trocar fonte/limitar escopo; nenhuma regra nova |
| **F1 Modelo de spot e invariantes** | Primeiro caso canônico com posições, pré-flop, 100BB alvo, ação e board, rake/sizing quando disponível, mãos possíveis, força relativa, histórico e limites de generalização | **BLOCKED** | Corrigir domínio, não inventar contexto |
| **F2 Aprovação estratégica de módulo** | Proposta apoiada por fonte(s) e lógica verificável; revisão de alternativa/contraexemplo; casos críticos (full house, flush, nuts, blefes, preço, sizings); explicação das concessões e cobertura | **BLOCKED** | DRAFT/REJECTED, não criar módulo aprovado |
| **F3 Fidelidade OpenPPL** | Uma fonte nativa, ação/precedência legal, símbolos e memória corretos, testes focados contra especificação independente, sem fallback ambíguo | **BLOCKED** | Corrigir tradução/routing sem reinterpretar fonte |
| **F4 Replay offline OpenHoldem** | Decisão planejada = observada = ação aceita; histórico/scrape e comportamento de erro verificados em ambiente desconectado | **BLOCKED** | Não declarar operacional |
| **F5 Produto / benchmark** | Abrangência real superior ao R10d nas 14 famílias; robustez e variações de stack/posição, avaliação de violações estratégicas, observabilidade e permissões de uso | **BLOCKED** | Não alegar superioridade, GTO ou prontidão |

**Contagem V2 aprovada: ZERO.** 14/14 famílias benchmark sem certificação V2. Checkpoint V1 permanece apenas histórico e não muda a contagem. Cada gate precisa ter decisão registrada com evidência/revisão; não há exigência geral de EV quantificado.

## 6. Ordem concreta de construção (após F0)

1. **Primeiro contrato completo simples:** RFI BTN 6-max 100BB, confrontando chart público admissível e baseline histórica por classes/combos; explicitar premissas de rake/sizing e política de mix; não transplantar valores ainda.
2. **Módulo pós-flop de maior retorno de generalização:** BTN PFR vs BB caller, SRP HU, c-bet IP em famílias de flop seco, wet e monotone; documentar valor, blefe, checks e sizes com fonte profissional. Reutilizar conceitos do DeepCrusher quando independentes de stack, isolando exceções por SPR.
3. **Sentinela anti-erro:** river four-flush com board pareado e full house; e sem board pareado com flush alto/baixo e bluff-catcher, incluindo check grátis, bets, raises e blefes. **Não criar percentual genérico de call** sem justificativa.
4. Expandir respostas a c-bets, turn barrel/probe/delayed c-bet, river value/bluff, 3bet HU, limped/iso, multiway, 4bet/5bet, profundidades e perfis. Sempre relacionar cenário, fonte, execução e lacuna frente ao R10d.

Uma regra pequena e correta tem prioridade sobre 200 regras de cobertura superficial. Reutilizar as abstrações/contratos V1 após auditoria; **não copiar estratégia V1 automaticamente**.

## 7. Registro vivo, critérios de parada e não-objetivos

- **Toda iteração:** ler este `v2/PLAN.md`, os ADRs em `DECISIONS.md`, `STRATEGY_ARCHITECTURE.md` e o catálogo de capacidades R10d; atualizar a fonte de verdade quando a decisão ou gate mudar. Não deixar documentos no GitHub esquecidos.
- Registro futuro por módulo: `spot_id`, URL/título e versão da fonte, hipótese de rake/stack/sizing, decisão, exceções, revisão contraditória, cobertura, autor da regra e estados `DRAFT`/`STRATEGY_REVIEWED`/`OPPL_PARITY`/`OH_OFFLINE_VERIFIED`.
- Uma divergência entre texto e código, classificação incorreta de mão, ação ilegal, fallback desconhecido ou incompatibilidade relevante de ranges **bloqueia promoção**.
- Regra de stop de compute: após duas análises repetidas que não acrescentem evidência, interromper e definir a próxima hipótese útil. Uma CI integral por incremento integrado; testes locais focados durante desenvolvimento.
- **Não** declarar bot GTO, performance em bb/100, winrate, exploitabilidade ou EV sem medição aplicável. Sem execução com dinheiro real em plataformas que proíbam bots/RTA.

## 8. Estado de retomada

- **ADR-044** substitui somente o requisito metodológico `solver-first` da ADR-043; mantém preservação V1, independência de evidência, controles OpenPPL/OH, benchmark R10d e gates de produto.
- F0 **OPEN**; F1–F5 **BLOCKED**; nenhuma política V2 aprovada. GTOpen/TexasSolver não são obrigatórios nem próximos passos.
- **Próxima tarefa:** construir o **catálogo F0 de fontes e premissas**, anotar incompatibilidades/licenças, e selecionar o primeiro spot de referência pública. Nenhum OpenPPL novo antes de F0/F1/F2.
- **Ação local do usuário:** nenhuma para a revisão de fontes/documentos; futura execução no OH só mediante necessidade concreta de F4.


## 9. F0 — evidência efetivamente examinada (21/11/2026)
- [Catálogo SRC-001–SRC-006 e fontes adicionais verificadas](SOURCES.md) contém **divergência não reconciliada** BTN RFI: Upswing 100BB 40,9%, Upswing online 6max 43,1% (profundidade não exposta no resumo), ART/GTO 100BB **2BB open** 46,5%. Não importar percentuais entre sizings, nem declarar qualquer um GTO da V2. Direitos de chart ainda em exame.
- [Caso de auditoria objetiva RIVER4_PAIRED_Q9_FULLHOUSE](cases/RIVER4_PAIRED_Q9_FULLHOUSE.md) identifica todos os tipos superiores plausíveis no board Q♠ J♠ T♠ 9♠ Q♥ com Q♦9♦: straight flush com K♠/8♠ e full houses superiores com Q♣Jx/Q♣Tx; Q♣9x empata. Invariante de ranking confirmado por raciocínio de cartas; **não** é EV/solver nem ação CALL universal.
- Defeito legado comprovado: `f$SRPStrongMade` retorna TRUE para `HaveFullHouse`; o seletor `NOT HaveFlush AND NOT HaveNuts` captura full house não-nuts; `Fold FORCE` genérico ocorre acima de 20% PotSize. A regra V1 continua arquivada, não corrigida in-place.
- Fontes profissionais de c-bet e bluff-catching apoiam contexto, preço, combos e histórico; nenhuma publicou a solução exata do caso ilustrativo. O projeto continua **F0 OPEN, F1–F5 BLOCKED, 0 regras V2 aprovadas**.
