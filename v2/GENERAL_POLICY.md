# DeepPoker V2 — Política geral de abstração e qualidade estratégica (ADR-049)

**Data:** 21/11/2026. **Status:** vigente para novas decisões. Subordinado a [PLAN.md](PLAN.md) e [DECISIONS.md](../DECISIONS.md). **Substitui a leitura literal de exemplos** nos ADR-045–048 sem apagar aqueles checkpoints. Nenhuma nova ação de pôquer é aprovada por este documento.

## 1. Intenção real e interpretação de exemplos

Exemplos apresentados pelo usuário **ilustram princípios transversais**; não são, por si, limites, testes exclusivos, metas de cobertura, percentuais exatos nem prioridades permanentes. Ao receber um exemplo, o projeto deve registrar:

1. **Princípio abstrato** que o exemplo tenta comunicar.
2. **Domínio em que vale**, isto é, posições, street, stacks, ranges, número de jogadores, rake/ICM, ações anteriores e tamanho da aposta.
3. **Contraprova ou exceção** que impede uma regra absoluta.
4. **Aplicação transversal** em várias famílias de decisão, não só na mão original.
5. **Critério de validação proporcional ao risco**, e o que mudaria uma decisão.

Não concluir "o usuário quer exatamente X%" quando citou X% como ilustração. Não concluir "somente esse full house importa" quando exemplificou uma decisão obviamente ruim. Não concluir "somente SRP c-bet pode ser reaproveitada" quando citou uma situação transferível do DeepCrusher.

## 2. Aproximação estratégica, e não ajuste de casas decimais

- **OBJETIVO:** usar soluções e princípios profissionais publicados para construir políticas **próximas na composição de range e nas ações relevantes**, não clonar frequências numéricas de cada combo.
- Se duas linhas são legitimamente mistas e a referência publicada indica ações próximas em qualidade, é válido usar uma **simplificação determinística ou mix estável por mão**. Documentar que se trata de aproximação e preservar diversidade de valor/blefe/check quando material.
- **NÃO** fixar tolerância universal de 3 ou 4 pontos percentuais. Uma diferença de 4 p.p. em ação rara e cara pode ser decisiva; diferença maior em mixes de EV semelhante pode ter pouco impacto. Examinar **impacto da decisão**, não apenas distância numérica.
- Buscar precisão adicional somente se: (a) muda call/fold, bet/check ou stack-off em circunstância relevante; (b) desbalanceia drasticamente valor/blefe, proteção ou defesa; (c) altera materialmente cobertura, risco ou EV segundo evidência existente; (d) há nova fonte diretamente aplicável.
- **OPEN RFI 2,5 BB** permanece um padrão prático do piloto onde aplicável, **não tamanho obrigatório em todo contexto**. A antiga banda **41–44% BTN** era ilustrativa e não é um gate numérico nem exigência exata; outras posições têm seus próprios ranges.
- Não executar solvers próprios; não inventar EV nem "frequência correta" sem fonte. **Não abolir matemática básica** necessária a pot odds, sizing e SPR.

## 3. Política transversal de prevenção de erros graves

Aplicar em **todas as streets, forças de mão, potes e stacks**:

1. **Integridade física:** detectar as 7 cartas válidas, a melhor mão de 5, rank e kickers, possíveis nuts e mãos superiores; usar bloqueios e cartas impossíveis corretamente. Falha de scrape/board = desconhecido, não estratégia.
2. **Integridade da situação:** identificar pot origin, posição, jogadores ativos, quem iniciou/apostou/pagou/raiseou, transições de street, stack efetivo/SPR, preço, ações legais e unidades monetárias.
3. **Raciocínio range-vs-range:** distinguir valor superior, inferior, blefes plausíveis e draws; uma ameaça possível não significa que o vilão tenha frequência suficiente de valor superior para justificar fold.
4. **Decisão específica ao contexto:** priorizar política especializada com evidência sobre guarda genérica de textura, limiar de bet ou etiqueta ampla ("strong made", "one-card flush possible").
5. **Contraditório:** questionar tanto calls/raises absurdamente agressivos quanto folds/checks excessivamente conservadores. Não instituir regras inversas igualmente absolutas ("nunca fold full house", "sempre apostar nuts").
6. **Ação e falha operacional:** fold sem aposta a pagar, raise ilegal, aposta com unidade errada, memória de outra mão, ação em estado desconhecido ou fallback OpenHoldem não auditado são erros bloqueantes.

**Classes de risco:** 
- **BLOQUEANTE:** ação ilegal, mão/nuts classificados erroneamente, histórico falso, fallback que opera sem política ou decisão claramente incompatível com hierarquia de mãos/preço.
- **ALTA:** stack-off sem contexto, overfold/overcall grosseiro, ausência sistemática de blefes ou calls de defesa, mesmo ramo usado indevidamente para multiway e heads-up.
- **MODERADA:** simplificações de frequência/sizing plausíveis mas sem demonstração quantitativa de EV.
- **BAIXA:** diferenças marginais de frequência que não mudam a classe de ação, a qualidade do range ou o risco conhecido.

Os testes precisam variar **a família de circunstâncias**, não somente o exemplo que revelou o defeito. Não supor monotonicidade universal do tipo "mão mais forte => bet maior": proteção, blockers, indução e range checking podem inverter a ação.

## 4. Reaproveitamento do DeepCrusher — teste de invariância condicional

**Inventário ancorado:** [DEEPCRUSHER_TRANSFER_AUDIT.md](DEEPCRUSHER_TRANSFER_AUDIT.md), no R10d SHA Git `9f9cba79cdb9dc4438895770cf61a450fb55d17c`. "Reaproveitável" não é sinônimo de "copiar literal".

Para cada função/estratégia original, verificar:
- **Invariante mecânica:** conceito que vale independentemente da modalidade, como identificar pot family/histórico, calcular pot odds, proteger legalidade, classificar cartas. Reutilizar a *arquitetura* após conferir semântica OH, não necessariamente o texto original.
- **Invariante estratégica aproximada:** lógica geral de valor, blefe, blocker, proteção, posição e nut advantage, *quando* ranges e SPR compatíveis. Reaproveitar como **hipótese**, conferir com literatura profissional.
- **Dependente de profundidade/economia:** thresholds em 8–25 BB, stack-off, shove/fold, equity realization, 3bet/4bet, sizings, níveis de rake/ante/ICM. **Não portar** números ou decisões sem reformulação para cash.
- **Específica de modalidade/plataforma:** Spin&Go 3-handed, tempo/estrutura de torneio, PT4/network, perfis pontuais ou regras exploratórias de jogadores. Não importar como estratégia padrão cash 6-max.
- **Legado desconhecido:** qualquer ramo de engenharia ou ação não testado em fonte profissional compatível fica **DRAFT/QUARANTINED**.

Uma mecânica pode ser reutilizável mesmo se uma ação estratégica que a utiliza não for. O contrário também vale: uma ideia profissional válida pode exigir nova observabilidade.

## 5. Construção por famílias, não por exemplos isolados

A unidade de construção será a **família estratégica com predicados, ações, contraexemplos e cobertura**. Exemplos de cartas específicas são *fixtures* que ilustram e testam a família — não a própria capacidade.

**Trilhas paralelas, sem alterar os gates de produto:**

- **Estratégia (F1/F2):** levantar famílias de pré-flop RFI/resposta/3bet/4bet/squeeze/limp; SRP/3bet/4bet/limped, HU e multiway; flop/turn/river; valor/blefe/defesa, blockers, texturas, SPR, histórico e perfis. Produzir contratos por famílias com referências aplicáveis e decisões de granularidade suficiente, sem exigir precisão de décimos.
- **Engenharia (F3/F4):** manter o piloto de dois flops como smoke test de traduções e memória; trabalhar em observabilidade e replay OpenHoldem real. **F4 continua bloqueado** sem ação observada; **isso não impede F1/F2 em outras famílias**.
- **Integração e produto (F5):** só declarar módulo funcional quando os dois ramos convergirem para **a mesma especificação revisada**, com ação final OH, cobertura do domínio e comparação contra o piso R10d.

**Próxima tranche estratégica concreta:** criar especificação de **defesa de mão/range e gestão de agressão por risco**, cobrindo mais do que o exemplo full house (nuts/strong value, value vulnerável, bluffcatchers, draws, blockers e air) ao longo de flop/turn/river, com transições de check/bet/raise e restrições heads-up/multiway. Em paralelo, auditar famílias mecânicas do DeepCrusher (história/board, pot odds, sizing, status do adversário) que dão suporte a todas essas ações.

## 6. Critérios de gates e parada (sem burocracia crescente)

- A partir desta decisão, **F1/F2 podem avançar em várias famílias** independentemente de F3/OH do piloto. Ações novas não viram `OPPL_PARITY` ou `OH_VERIFIED` sem evidência.
- Cada família exige **fonte profissional** ou lógica objetiva, limites, contraprova, estados alcançáveis, decisão/size/ação legal e pelo menos teste para o risco principal. Não exigir prova solver de cada ação.
- Se análise adicional está debatendo apenas décimos de frequência/size sem evidência de mudança material, **PARAR** e executar o próximo incremento de cobertura.
- Se vier uma alteração que introduz erro estratégico grave ou degrada estado/histórico, **BLOQUEAR** promoção mesmo com CI verde.
- **Não medir sucesso por número de regras, por número de testes ou pelo caso individual ilustrativo.** Medir famílias reais de decisões utilizáveis e revisadas; manter 14 capacidades do benchmark R10d como piso de abrangência, não certificação GTO.
- **Não usar bot em mesa real** até permissões da plataforma, avaliação operacional, segurança e gates de produto estarem demonstrados.

## 7. Efeito sobre decisões anteriores

- **ADR-044/045:** uso de fontes profissionais sem solver permanece.
- **ADR-046:** manter praticidade no pré-flop e piloto, mas a banda 41–44% não é um alvo global. Simplificação é princípio geral.
- **ADR-047/048:** os dois spots F2/OpenPPL e seus 20 testes continuam válidos como engenharia estática, **não como prioridade exclusiva** e não como bloqueio da pesquisa estratégica independente.
- **F0 PASS_CONCEPTUAL**, **DATASET_IMPORT_HOLD**, **F1 PASS_PILOT_CONTEXT** em seu contexto, **F2 OPEN** com 2 decisões revisadas, **F3 STATIC_SYMBOLIC_VERIFIED/OH_PENDING**, F4/F5 BLOCKED; **ZERO módulos estratégicos completos aprovados**.
