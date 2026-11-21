# DeepPoker Strategy V2 — plano vivo proof-first

**Data da decisão:** 21/11/2026. **Estado:** RECOMEÇO AUTORIZADO; FUNDAÇÃO DOCUMENTAL; NENHUMA ESTRATÉGIA V2 APROVADA.
**Fonte única para o reinício:** este arquivo. Os documentos raiz apontam para ele. Manter os checkpoints históricos legíveis e imutáveis até eventual decisão técnica específica.

## 1. Diagnóstico e motivo do reinício

O código anterior passou por 611 testes e por CI de integridade, mas uma regra recém-integrada poderia desistir com full house num board de quatro cartas do mesmo naipe. Os testes asseguravam conformidade com *uma especificação estratégica equivocada*. Nenhuma evidência de solver, EV, exploitabilidade, paridade OpenHoldem real ou superioridade ao DeepCrusher_R10d tinha sido demonstrada. Isso invalida a **presunção de qualidade das decisões**, não a utilidade de arquivos técnicos, bibliotecas, C++/OpenPPL, infraestrutura ou dos testes de sintaxe.

**Decisão V2:** não partir da estratégia ISODEF/M08-RIVER4 para adicionar regras. Todo código V1, inclusive ranges v0.6.1, tem o estatuto **LEGACY_UNVALIDATED** para fins de qualidade estratégica. Conservar Git history, sem apagar ou reescrever histórico e sem promover nenhum `.oppl` existente. A V1 não é bot operacional.

## 2. Objetivo, restrições e definição operacional de qualidade

**Objetivo:** construir política 6-max NLHE cash *aproximada a uma referência solver* no conjunto explícito de situações cobertas, com avaliação reproduzível de perda de EV, robustez e ação legal no ambiente OpenHoldem. O requisito posterior de abrangência/qualidade superior ao DeepCrusher_R10d continua sendo objetivo de produto, **não alegação antecipada**.

**Separar conceitos:**
- *Corretude da implementação* = interpreta/compila/parsa e seleciona ações conforme o contrato; testes de software.
- *Qualidade estratégica* = frequências por combo e nó, valor esperado, vulnerabilidade à exploração, linhas/call/fold em contextos reais de ranges e rake; requer referência matemática/experimental.
- *Robustez operacional* = símbolos observados, memória, ação tentada, ação aceita e comportamento em erro; exige teste local offline e condições de uso permitidas.
- *Lucratividade/superioridade no mundo real* não segue de nenhum dos três isoladamente.

Nunca usar a expressão 'próximo de GTO' sem especificar **qual jogo abstrato**, tamanho das árvores, ranges de entrada, rake/cap, tolerância de convergência, cobertura das linhas e métrica de desvio. Solver não é oráculo fora de seu jogo/modelagem.

**Plataforma:** OpenPPL nativo segue como formato-alvo de política; Python pode fazer extração, geração determinística, validação e pesquisa **offline**, não fornecer independentemente a política de decisão no runtime. Não usar assistência durante jogos em plataformas que proíbem bot/RTA. Estudo e teste desconectados primeiro.

## 3. Fontes externas candidatas e limites conhecidos (ainda NÃO validadas)

- **GTOpen** — `MatthewPDingle/GTOpen`, licença Apache-2.0 segundo repositório público, solver Rust/CUDA/CPU. Documentação anuncia postflop HU com DCFR/CFR, card removal e cálculo de best response; preflop 2–9 jogadores tem **modelo de continuação aproximado** para pós-flop e limitações multiway/169 classes; 3way beta. **Candidato prioritário para estudo de viabilidade, não autoridade validada.**
- **TexasSolver** — `bupticybee/TexasSolver`, referência técnica para segunda implementação de pós-flop HU independente. Confirmar versão/licença/formato/escopo antes de distribuir dados ou integrá-lo. Não exigir cruzamento numérico absoluto sob abstrações diferentes.
- **GTO Wizard** — pode orientar estudo autorizado, **não** copiar ou monetizar árvores/charts sem direitos de uso; termos vedam real-time assistance em jogo vivo e monetização de soluções obtidas. Não depender dele como dataset de produção sem licença explícita.
- **DeepCrusher_R10d** — repositório próprio, baseline de abrangência **heurística**, não gabarito GTO; comparar somente em condições equivalentes, sem copiar automaticamente suas ações.

Nada acima foi instalado, executado nem validado em máquina do usuário nesta etapa.

## 4. Pipeline: da evidência à ação, na ordem obrigatória

```text
Definir jogo/regras/rake/árvore/ranges
        ↓
Resolver + verificar convergência e consistência econômica
        ↓
Arquivar soluções com proveniência e cobertura
        ↓
Projetar compressão/abstração para OpenPPL
        ↓
Avaliar EV perdido e frequências por combinação/nó
        ↓
Gerar módulo OpenPPL nativo + testes de paridade offline
        ↓
Comprovar parsing, símbolos e ação final em replay OpenHoldem desconectado
        ↓
Aumentar cobertura; avaliar contra DeepCrusher_R10d e outros baselines
```

É PROIBIDO inverter a ordem (inventar percentuais de call/raise/blefe e só depois criar testes que os confirmem).

## 5. Gates vivos: cada um tem aprovação, bloqueio e parada

| Gate | Evidência mínima para PASS | Estado inicial | Se não passar |
|---|---|---|---|
| **F0 Viabilidade de solver** | Um cenário postflop reproduzível; condições, recursos, convergência, saída por combo e licença documentadas; nenhum número inventado | OPEN | Sem codificar política; mudar ferramenta ou reduzir piloto |
| **F1 Dados de referência e jogo** | Inputs completos: 6max 100BB, blind 0.5/1, *rake/cap especificados*, ranges por combo, linha até o nó, ações/sizes; licença dos dados | BLOCKED | Não chamar ramo de referência GTO |
| **F2 Fidelidade estratégica** | Frequências de fold/call/bet/raise por combo, EV de cada ação, perdas por compressão e outliers; holdouts pré-especificados; linha de nuts/full house não abstraída erroneamente | BLOCKED | Rejeitar ramo, nunca reduzir testes para 'aprovar' |
| **F3 Implementação OpenPPL** | Uma fonte nativa, parsing/símbolos, transições/first-match/no-match, legalidade, paridade com especificação e invariantes de mão fortes | BLOCKED | Corrigir mapeamento, não retocar solver para encaixar no código |
| **F4 Operação desconectada** | No OpenHoldem real de teste: estado observável, ação calculada, ação tomada, ação aceita, comportamento de erro; sem depender de hash privado para construir | BLOCKED | Não declarar operacional |
| **F5 Produto** | Cobertura de decisões comum/rara, EV e métricas de robustez em situações equivalentes, comparação explícita ao R10d, nenhuma métrica inferida só de tamanho de código | BLOCKED | Não afirmar superioridade nem jogar por dinheiro |

**Evidência de F0 não é F1; passar testes de código não passa F2; 0/14 R10d VERIFIED na V1 continua 0/14 para qualquer alegação V2.**

## 6. Experimento zero (P0), custo baixo e stop rule

**Pergunta experimental:** é possível obter, reexecutar e inspecionar uma solução solver de river HU, com ações e EV por combinação, para um cenário fixo que o antigo sistema tratava mal?

**Plano técnico:**
1. Avaliar montagem/build e saída real de pelo menos um solver candidato; anotar hash/revisão do solver e parâmetros e limites de RAM/CPU. Se isso falhar, **parar**; não implementar nenhuma nova regra.
2. Configurar cenário artificial *apenas de fumaça* com board e ranges conhecidos e pote/stacks explícitos: quatro cartas de um naipe, caso com board pareado e caso sem board pareado; verificar card removal, mãos legais e classes de mão. Esse smoke **não certifica** estratégia porque a distribuição de ranges até o river pode não ser realista.
3. Rodar solver para o mesmo jogo em múltiplas precisões até observar estabilização. Ler as estratégias de **nut flush, flush não nut, full house, set, two pair, bluff-catcher e blockers**, separando posições e oponentes. Usar EV das *ações* para justificar frequências, nunca aplicar um limiar arbitrário de pote.
4. Se F0 funcionar, antes de F1 escolher a variante completa 6max cash, rake real/cap, ranges pré-flop confiáveis, árvore de sizings e linha flop→turn→river. **Sem isso, não existe validação de estratégia 6max.**
5. F2: comparar solução de referência e aproximação candidata em **conjunto de desenvolvimento e conjunto holdout separado**, ambos derivados de cenários declarados. Critérios numéricos definidos antes da medição, em unidades de pot/bb. Se o budget de erro não puder ser definido de forma justificável, **não promover**.

**Critérios absolutos de parada:** solver sem resultado reproduzível, parâmetros não rastreáveis, dados de terceiros sem direito de reutilização, incapacidade de calcular perdas de EV, ação ilegal, confusão de força de mão, árvores que ocultem parte material das ações ou custo de computação claramente desproporcional. Poderemos optar por escopo menor; não rebaixar a qualidade silenciosamente.

**O primeiro artefato estratégico V2 não será um .oppl. Será a solução de referência validada de P0/F0, com seus parâmetros e limitações.**

## 7. Processo enxuto e responsáveis

- **IA/engenharia:** estudar duas ferramentas, definir entradas, construir pipeline de extração e auditoria matemática, explicar concessões quantitativas, apontar falhas. Nunca inventar recomendações solver ou classificar teste unitário como prova GTO.
- **Usuário:** decidir o compromisso de produto quando surgirem escolhas reais (stakes/rake/ambiente permitido) e fornecer hardware ou saídas apenas quando indispensáveis ao experimento, não ao planejamento. Nenhuma ação local exigida para abrir a V2.
- **GitHub:** esta página é viva. A cada gate alterado registrar fonte, commit, resultado e motivo, não empilhar 20 relatórios redundantes. Arquivos legados permanecem consultáveis; nova estratégia deve residir apenas em `v2/` até aprovação; não modificar prematuramente `benchmarks/r10d_floor/PROMOTION_GATE.json`.
- **CI:** teste localizado durante exploração; uma regressão integral ao integrar um incremento. Não rodar múltiplas execuções sem pergunta técnica específica.
- **Monitoramento de tempo/compute:** se duas tentativas de ferramenta com problema da mesma natureza não oferecerem evidência nova, parar e decidir alternativa explicitamente.

## 8. Estado ao criar o documento

- F0 **OPEN**, F1–F5 **BLOCKED**.
- Solver escolhido **PROVISÓRIO**: testar GTOpen primeiro; TexasSolver é candidato de cross-check/contingência. Nenhum deles foi executado.
- V2 estratégica **nenhuma linha aprovada**, nenhuma estratégia ativa para operar em mesas.
- Preservado `main` V1 até a integração documental; não apagar a V1.
- Próxima ação técnica: reproduzir **um solve de river HU, dados por combo e EV**, armazenar parâmetros e decidir F0 com evidência, em vez de voltar diretamente à geração de OpenPPL.
