# V2 — Registro vivo de decisões e revisão obrigatória

**Status:** fonte auxiliar vinculante do [Plano Vivo](PLAN.md). [DECISIONS.md](../DECISIONS.md) preserva o histórico integral das ADRs; este registro mantém seu **estado atual, conflitos e dependências**. Atualizado: **22/11/2026 — ADR-053**.

## Protocolo permanente — antes de CADA nova decisão técnica

1. **Ler o estado mais recente do [PLAN.md](PLAN.md)**, este registro e a parte aplicável de [DECISIONS.md](../DECISIONS.md), além do código-fonte atualmente candidato. Consultar [HANDOFF.md](../HANDOFF.md) e [STRATEGY_ARCHITECTURE.md](../STRATEGY_ARCHITECTURE.md) se a decisão alterar rumo, interface, histórico ou cobertura.
2. **Revisar decisões prévias pertinentes, não apenas ler os títulos.** Para cada uma: ainda válida? há nova evidência? mudou o objetivo/requisito? a proposta viola invariantes anteriormente demonstrados?
3. **Registrar o contraditório antes da edição material:** opção atual, alternativa considerada, evidências, custo e riscos de ambas; recomendação e razão de manter ou mudar. Perguntas e exemplos do usuário não equivalem a autorização de pivô.
4. **Registrar a nova decisão antes ou junto com o código:** identificador ADR, arquivos afetados, condições, critérios de parada, risco, escopo que NÃO está resolvido e próximo passo. Sempre indicar se uma decisão anterior foi **mantida, refinada, parcialmente substituída ou revogada**.
5. **Atualizar o mesmo conjunto de documentos**, não criar um arquivo que depois ninguém consulta: `v2/PLAN.md`, `DECISIONS.md`, este registro, `HANDOFF.md`, `PROJECT_STATE.md` e notas de versão. Quando necessário atualizar `ROADMAP.md`, `STRATEGY_ARCHITECTURE.md`, `README.md` e `RELEASE_MANIFEST.md`.
6. **Não confundir teste estático, leitura do manual, ação final no OpenHoldem e qualidade estratégica.** Fazer checagens proporcionais ao risco sem impedir o desenvolvimento por certificações acadêmicas. Nenhum módulo passa a "pronto para jogar" só porque código ou CI existem.
7. Em nova retomada, **este arquivo e o Plano Vivo são obrigatórios antes de construir qualquer coisa**. Não reiniciar o roadmap nem esquecer as decisões ou os arquivos que as materializam.

## Decisões pertinentes — revisão realizada nesta rodada

| Decisão anterior | Estado agora | Revisão e efeito na ADR-053 |
|---|---|---|
| **ADR-001 / ADR-044** — heurística sem solver próprio | **MANTIDAS** | Histórico é observabilidade, não convite para instalar GTOpen/TexasSolver; não publicar winrate/GTO sem evidência |
| **ADR-002** — GitHub como fonte de verdade, documentos vivos | **MANTIDA E REFORÇADA** | Institui esta tabela de revisão e links no topo do Plano/Handoff para evitar decisões esquecidas |
| **ADR-004** — política ausente não equivale a Fold/Check estratégico | **MANTIDA** | Classificador desconhecido é **UNKNOWN**, não "adversário passivo"; regras de fallback existente continuam candidato inseguro |
| **ADR-049** — exemplos são princípios gerais | **MANTIDA** | Pergunta do usuário sobre river gera implementação transversal de histórico em **todas as streets**, não regra pontual de river |
| **ADR-050** — entregar bot e usar feedback, sem certificação acadêmica | **PARCIALMENTE SUPERADA pela ADR-051** | Cadência pragmática permanece; a afirmação de que v0.1 estava pronta foi **REVOGADA**, não deverá reaparecer como estado vigente |
| **ADR-051** — v0.1 retirada; corrigir lógica objetiva | **MANTIDA** | Histórico precisa ser baseado em semântica real de OpenPPL, não rótulos intuitivos ou memórias que não garantem ação final |
| **ADR-052** — v0.3 corrige odds/SPR/nuts/draws, ainda candidata | **MANTIDA; v0.3 preservada** | Nova v0.4 é derivação, não sobrescrita; preserva correções de risco já aprovadas como necessárias |
| **V1 HIST-1**, documentada em STRATEGY_ARCHITECTURE | **REFERÊNCIA DE ENGENHARIA, NÃO POLÍTICA IMPORTADA** | Conceito de histórico por sequência é aproveitável; não importar thresholds ou assumir 9 topologias V1 cobrem cash 6max |
| **ADR-053** — histórico nativo com escopo de confiança | **VIGENTE, EM IMPLEMENTAÇÃO** | Ver [HISTORY_MODEL.md](HISTORY_MODEL.md); v0.4 marcada HISTORY_REVIEW, sem liberação para jogo |

**Nota sobre documentos legados:** banners antigos que dizem “ADR-050 VIGENTE” ou “v0.1 pronta” são **registros históricos superados**, não instruções atuais. A decisão atual é sempre a mais recente não revogada nesta tabela e no cabeçalho do Plano Vivo. Manter o histórico, mas eliminar ambiguidades em novos checkpoints.

## ADR-053 — comparação das alternativas e decisão

**Requisito explícito:** registrar **todas as decisões** e **revisitá-las antes de novas decisões**. Além disso, o bot deve considerar o histórico de pré-flop/flop/turn antes de decidir no river, sem inferir a identidade do vilão em uma mão que começou multiway.

**Opção A — criar máquina paralela própria `me_st_` com snapshots por ação:** permite customizar tamanhos, posição e histórico detalhado, mas acarreta reset manual, falsas transições por frames, duplicação da engine e risco de contaminar a próxima mão. Não escolher como caminho inicial.

**Opção B — usar exclusivamente os marcadores `user_` para todas as ações:** simples, porém `Set user_` só prova intenção durante avaliação da fórmula; pode ser falso como descrição da ação executada. Além disso, adversários podem agir enquanto a fórmula do Hero não está sendo avaliada. **Não recomendado como única fonte.**

**Opção C — reconstrução híbrida fonte-primeiro com símbolos históricos nativos e `user_` somente para intenção:** **RECOMENDADA**. Implementar classificadores HU-from-flop usando `OpponentCalledOnFlop`, `NoBettingOnFlop`, `NoVillainBetOrRaisedOnFlop`, `BotCalledOnFlop`, `BotRaisedOnFlop`, equivalentes de turn, e preço atual; `user_DP_PF_RFIIntent` separado de `BotRaisedBeforeFlop`. Usar `NoBettingOnFlop` corretamente (inclui apostas do Hero) e restringir predicados que atribuem apostas ao mesmo adversário a `OpponentsOnFlop=1` e `OpponentsLeft=1`.

**Evidência técnica:** no Manual OpenPPL, seção *User-Defined Variables*, `Set user...` continua a avaliação, persiste apenas por mão e não garante ação realizada. O capítulo *BettingAction Symbols* define `OpponentCalledOnFlop` e ressalva que contadores dependem de atualização após ação do autoplayer. Na biblioteca integrada OpenPPL fornecida, `OpponentCalledOnFlop` usa `didraisround_flop + didbetsizeround_flop == 1` junto com ausência de aposta/raise do vilão; `NoVillainBetOrRaisedOnFlop` consulta `raisbits_flop`. O manual OpenHoldem alerta que históricos podem falhar com hand reset incorreto. Isso sustenta o modelo e seus limites; **não** certifica execução no OH do usuário.

**Mudança estratégica limitada nesta tranche:** diferenciar *primeira aposta river após flop/turn passivos* de contextos agressivos ao responder com par forte em HU, sem alegar EV mensurado. Os **blefes de draws** exigem que a aposta do Hero de fato ocorreu e foi paga, em vez de confiar apenas no marcador de intenção. A classificação de triplo barrel fica disponível, **mas ainda não justifica por si só uma regra universal de fold/call**; a composição de range por linha será o próximo trabalho. Nenhuma nova tabela GTO ou cálculo de solver.

**O que mudaria a decisão:** prova de que a biblioteca nativa usada pelo usuário não atualiza os símbolos de histórico de forma consistente, necessidade operacional de tamanhos/ator que a engine não conserva, ou evidência de que um ramo de política histórica produz decisões piores. Só então justificar outro armazenamento, com reset, auditoria temporal e isolamento por mão.

**Estado final desta ADR:** `HISTORY_REVIEW`, ainda sem prova de execução OpenHoldem, sem promoção para jogo e sem alteração do código V1.
