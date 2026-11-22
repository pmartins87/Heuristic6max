> **VERSÕES (22/11/2026):** v0.1 **REVOKED_FOR_PLAY**; v0.2 **LOGIC_REVIEW histórica**; [v0.3 CONTEXT_REVIEW](DeepPoker_V2_Cash6max_v0_3_CONTEXT_REVIEW.oppl) é **candidata com correções estruturais, ainda não recomendada para jogo**. [O que mudou e o que falta](LOGIC_REVIEW_20261122.md). As instruções de carregamento da v0.1 abaixo são HISTÓRICAS, não devem ser seguidas.

> **AVISO CRÍTICO — 21/11/2026 / ADR-051:** a v0.1 descrita abaixo foi **reprovada para uso em mesas** após identificação de falhas objetivas graves. **NÃO carregue a v0.1 para jogar.** Este README é histórico da entrega prematura. [Revisão lógica](LOGIC_REVIEW_20261121.md) e [candidata v0.2 não liberada](DeepPoker_V2_Cash6max_v0_2_LOGIC_REVIEW.oppl). Não existe neste momento uma versão V2 pronta para operação.

# DeepPoker Strategy V2 Cash6max — v0.1.0

**STATUS HISTÓRICO REPROVADO:** a v0.1 possui quatro streets preenchidas, mas demonstrou falhas graves na lógica do pôquer e **NÃO é recomendada para testes em mesas**. **Não foi executada aqui no OpenHoldem real.** Não é solver, não afirma GTO exato, bb/100, lucro ou certificação científica.

**Arquivo único para carregar:** [DeepPoker_V2_Cash6max_v0_1.oppl](DeepPoker_V2_Cash6max_v0_1.oppl)

## O que faz

- **Pré-flop:** RFI por LJ/HJ/CO/BTN/SB (tabelas heurísticas por classe de mão); RFI 2,5BB como padrão, 3BB no SB; resposta a open por posição/preço; BB defendendo mais mãos vs posições tardias; 3-bet/4-bet/5-bet e call de 3-bet; isolamento de limpers, overlimp seletivo e check gratuito no BB. Não exige frequência decimal exata.
- **Flop:** distingue iniciativa pré-flop, heads-up/multiway, textura dinâmica, força da mão, draws, c-bets de valor, air em frequência moderada, defesa contra apostas, check-raises e semi-bluffs.
- **Turn:** política de value/barrel/check, probe/delayed-cbet seletivo, draws com preço, resposta a agressão, controles de SPR e riscos da textura.
- **River:** aposta por valor com mãos feitas, thin value com pares fortes, bluffs seletivos de draws que apostaram antes, calls específicos por força/price/board. **Full house não pode cair num fold genérico só porque o board está four-flush**.
- **Fallback definido:** ao chegar ao final de uma street, check com preço zero / fold quando há aposta a pagar. **Não depende intencionalmente do `default.bot`** para estados que não acionaram nenhum ramo.
- **Limite de jogo:** só aplicar a mesas de **até seis jogadores que receberam cartas**. O código tem barreira de 7+ jogadores.
- **Stacks:** referência cash 100BB, com ramos cautelosos por SPR e compromisso; 200BB pode ser usado como teste, mas **não tem calibração deep-stack específica** nesta versão.

### Fontes e engenharia reaproveitada

As **listas RFI foram escritas como uma aproximação heurística original** à estrutura dos ranges cash 6-max divulgados por [Upswing](https://upswingpoker.com/preflop-open-strategy-rfi-explained/) e [Poker Skill](https://www.pokerskill.com/charts/preflop/). Não são cópias de um arquivo de soluções proprietário e não reproduzem frequências GTO por combo.

Os conceitos de c-bet/check em boards dinâmicos e multiway foram informados por [GTO Wizard — IP C-bet heuristics](https://blog.gtowizard.com/flop-heuristics-ip-c-betting-in-cash-games/) e [GTO Wizard — blockers](https://blog.gtowizard.com/understanding-blockers-in-poker/). As ações e limiares específicos restantes são **heurísticas da V2 ainda não comparadas a uma estratégia profissional por nó**. Não inferir EV positivo só porque a ideia é coerente. A arquitetura foi inspirada na separação histórica/pot/hand do [DeepCrusher_R10d](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt) **sem** copiar regras short-stack de Spin & Go.

## Procedimento histórico de v0.1 — NÃO seguir; versão revogada

1. **NÃO EXECUTAR ESTES PASSOS NA v0.1.** O trecho seguinte permanece apenas para registrar instruções que foram dadas prematuramente. Referência antiga: o arquivo `.oppl` acima (GitHub → Raw/Download), preservando a extensão.
2. Abra o OpenHoldem, use **File → Open** (ou o editor de fórmulas) e selecione o arquivo. Com `f$preflop` não vazia, a documentação do OpenHoldem informa que a fórmula entra no modo **OpenPPL**; a biblioteca OpenPPL integrada precisa estar presente.
3. Se quiser conferir antes de habilitar ações, mantenha o **autoplayer desligado** no início e observe as decisões em uma mesa de demonstração ou ManualMode. Depois faça o seu teste somente em um ambiente em que o uso de bots seja permitido.
4. Se houver erro, envie **a mensagem literal do parser**, a versão do OpenHoldem e, de preferência, a linha/estado de uma mão em que a decisão foi inadequada. Eu corrigirei a fonte e publicarei a versão seguinte no mesmo repositório.

**Não precisa de certificação acadêmica, mas a estratégia precisa respeitar as regras objetivas do pôquer antes de ser usada.** O fluxo pretendido era **entregar → testar → observar problema concreto → corrigir**, com checagem básica de sintaxe ao editar para evitar erros óbvios.

## Limites e riscos conhecidos (não escondidos)

- Não houve carregamento do executável OpenHoldem neste ambiente. O código usa os símbolos e formatos documentados nos manuais fornecidos; o build do seu OH pode diferir.
- Não há reads estatísticos confiáveis de adversários, integração com tracker, exploração ajustada por população, rake próprio de uma sala, ICM ou gestão de banca.
- Este é um **perfil genérico e inicial**, não um especialista GTO resolvido; algumas decisões (principalmente raises grandes/river e potes 3bet multiway) precisarão ser refinadas com exemplos profissionais, seu feedback e maior cobertura de tipos de pote.
- O OpenHoldem pode ajustar uma aposta solicitada por mínimo/máximo permitido; uma ação final incorreta pode ser do tablemap, do runtime ou da fórmula. O log exato ajuda a separar.
- Uma fórmula tecnicamente completa **não equivale** a uma estratégia lucrativa. Nem a V1 nem o R10d são gabaritos de EV para cash 6-max.
- Não usar para violar regras de salas ou sites. O modo como o OpenHoldem interage com o cliente depende de tablemap e configuração do usuário, **não** de arquivos adicionais criados aqui.

## Versionamento e continuidade

- **v0.1.0:** primeira base jogável e independente nas quatro streets, com 16 handlists, 20 helpers de contexto/força/SPR e política explícita nos quatro callbacks.
- **V1:** intacta no repositório, considerada legado de estratégia não validada.
- **Piloto F3 de dois flops:** preservado em [../pilot_01](../pilot_01) como exemplo de engenharia, **não obrigatório para usar esta V2**.
- **Próximas melhorias:** corrigir erros reais do usuário, aprofundar ranges em potes 3bet/4bet, multiway, river e stacks diferentes, e avaliar módulos do DeepCrusher caso sejam realmente transferíveis. Não gastar ciclos ajustando casas decimais sem impacto relevante.

**Fonte de verdade do projeto:** [v2/PLAN.md](../PLAN.md), [v2/GENERAL_POLICY.md](../GENERAL_POLICY.md), [ADR-050 em DECISIONS.md](../../DECISIONS.md). Manter estes documentos atualizados após cada alteração relevante.
