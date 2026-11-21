# Heuristic6max — arquitetura de um bot COMPLETO, sensível ao histórico

**Fonte de verdade do objetivo e escopo — 20/11/2026.** O projeto é **um bot de poker de engenharia complexa**, com milhares de caminhos de decisão e heurísticas inspiradas no GTO. Não é um solver nem um experimento científico. **Excelência estratégica é a meta**, nunca uma propriedade presumida pela quantidade de regras ou testes.

## Núcleo da estratégia (requisito, não simplificação)

Cada decisão precisa ser condicionada por: street, quantidade/posição dos jogadores, tipo de pote e árvore pré-flop, papel do Hero (agressor/caller), histórico da mão (ações do Hero e dos oponentes em ordem e tamanho), SPR/stack efetivo, textura de board e runout, força relativa da mão/draws/blockers, frequência/size de apostas e comportamento observado do adversário. Sem esse histórico, uma regra genérica de “top pair” é uma exceção conservadora/provisória, não arquitetura final.

A unidade de implementação é um **nó de um grafo de decisões**, não um número fixo de ifs independentes. Cada nó tem chave canônica, evidências de estado, ações legais, tamanho/frequências, histórico anterior, política de prioridade, marcador DRAFT/VERIFIED e testes específicos. Não criar estados impossíveis só para inflar a contagem. Reutilizar helpers e handlists OpenPPL para centenas/milhares de combinações efetivamente alcançáveis.

## Eixos de cobertura (expansão gradual sem pivô)

| Eixo | Famílias exigidas no produto final | Situação no checkpoint atual |
|---|---|---|
| Pré-flop | RFI, VS_OPEN, VS_3BET, VS_4BET/5BET, limp/iso, cold-call, squeeze, shove, stacks variados | RFI/VS_OPEN/VS_3BET DRAFT; demais pendentes |
| Tipos de pote | SRP, 3-bet, 4-bet, 5-bet, limp/iso, multiway | SRP HU parcial |
| Streets | Flop, turn, river, incluindo transições e mudanças de iniciativa | Três streets em G3; HIST-1 adiciona duas transições explícitas |
| Linhas de aposta | check-through, bet-call, bet-raise, check-raise, delayed c-bet, double-barrel, probe/donk, raise-call, bets por tamanho | HIST-1 cobre apenas B/C/X simples × B/C/X simples (9 sequências) |
| Board | paired/unpaired, flush/straight draws/completed, conectividade, textura e mudanças no turn/river | Só sinais gerais no MVP G3 |
| Estratégia | value, bluff, semi-bluff, bluff-catch, blockers, proteção, equity realization, range advantage, pot odds e sizing | Heurísticas iniciais; estratégia ainda DRAFT |
| Adversários | posição, range, perfil, tendências por ação/tamanho, amostra mínima e fallback conservador | Não implementado |
| Operação | parsing OH, log de histórico íntegro, ações legais, no-match seguro e replays offline | Ainda bloqueado no executável real |

**Regra de decisão técnica:** completar um eixo não equivale a terminar o bot. Não alterar o baseline pré-flop para forçar taxa agregada de um benchmark incompatível. Dados novos mudam a política apenas após checagem coerente e regressão; não exigir estudo de EV rigoroso para cada heurística DRAFT. Priorizar perdas graves causadas por falhas de histórico, decisões ilegais, sizings e ausência de resposta.

## Continuidade implementada

- `gto6_heuristic_v0_6_1/` é a referência histórica preservada para RFI, VS_OPEN e VS_3BET.
- `portability/srp_hu_mvp/` é o pós-flop G3 original, igualmente preservado.
- `portability/srp_history_v1/` **não substitui** o anterior: acrescenta 9 classes de trajetória flop→turn e regras particulares de turn/river, com fonte OpenPPL única e gerador offline.
- Versões históricas e novos módulos devem permanecer reprodutíveis. Consultar e atualizar este arquivo juntamente com `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md`, `CHANGELOG.md`, `RELEASE_MANIFEST.md`, `PORTABILITY_CONTRACT.md` e `README.md` a cada checkpoint importante.

## Critérios práticos de conclusão

1. **Cobertura:** nenhum estado do domínio anunciado sem regra de decisão e sizing aplicável; nós desconhecidos identificados e tratados explicitamente, sem fallback silencioso do OH.
2. **Histórico fiel:** eventos anteriores da mão, tipos de pote e ações do Hero/vilão coerentes inclusive em reavaliações e trocas de street; distinguir desconhecido de falso.
3. **Portabilidade:** fonte de ação em OpenPPL, não duplicação Python; confirmar símbolos e ação final no OH-alvo em replay desconectado de apostas.
4. **Qualidade:** medir erros graves de estratégia, consistência de ranges, adaptação a posição/stack/rake/sizing, revisão contra charts compatíveis, testes com diversas classes de oponente e amostras reais simuladas/observadas, sem alegar solução ótima.
5. **Entrega:** funcionamento de ponta a ponta em todo domínio alvo, documentação e regressão, rollback e logging — não simplesmente milhares de linhas OpenPPL.

## Sequência imediata

**HIST-1 (este checkpoint):** 3 estados exclusivos do flop × 3 do turn, 9 trajetórias, regras específicas, guardas para não classificar raise como c-bet, 18 testes. **HIST-2:** captura canônica de ações intra-street e posições de agressor/caller, bet-raise/call e check-raise. **HIST-3:** board texture/runout, SPR e sizings sobre essas linhas. **HIST-4:** 3bet/4bet/multiway/limped, além de perfis. **OH runtime:** validar paralelamente sem impedir a autoria dos módulos DRAFT, mas impedir qualquer alegação de bot pronto antes de um replay de ponta a ponta.

## G3-HIST-v2 — atualização do roadmap vivo (20/11/2026)
- **Entregue em DRAFT:** 6 famílias de histórico em flop e turn: B=bet-call, C=check-through, X=call, R=raise sobre bet, H=check-raise e M=bet→raise→call. **36 trajetórias** para o river, 70 helpers e 75 regras pós-flop, todas OpenPPL. Regressão preserva os 9 caminhos HIST-v1.
- **Não confundir classificação de flags com reconstrução exata:** podem existir ações adicionais dentro da mesma street; no-match continua inseguro em OH. O próximo objetivo é HIST-2b: reconstrutor cronológico/estado persistente e identificação de pote antes de construir a multiplicação de contextos (board, SPR, sizes).
- **Qualidade > contagem:** milhares de ramos só são úteis quando alcançáveis, semanticamente corretos e conectados às decisões relevantes. Esta versão não implica GTO exata nem excelência estratégica demonstrada.

## HIST-v3 — histórico cronológico como dimensão primária (ADR-026)
- Modelo base: sequência ordenada de eventos `(street, actor, action)`, Hero IP/OOP, Hero PFR/caller. Inventário finito com até quatro raises por street: **484 palavras de dois rounds que chegam ao river**, sem all-in, stacks, sizing, multiway ou ação estratégica imputada. [Matriz](portability/srp_history_v3/HIST3_484_CHRONOLOGICAL_PATHS.csv).
- Os 36 caminhos antigos eram combinações de flags agregados e são insuficientes; [3 colisões](portability/srp_history_v3/HIST3_OBSERVABILITY.csv) provam que não é possível reconstruir todo o histórico sem memória/eventos adicionais. `Set user` em OpenPPL + `BotsLast*Action` é o primeiro bridge, ainda não validado no executável real.
- A leitura do DeepCrusher_R10 e dos artefatos R10d foi **referência de complexidade e proveniência**, não fonte para transplantar ranges/heurísticas. Os 331 contratos de validação pós-flop históricos e 1.271 funções/listas R10d não são diretamente números de trajétorias comparáveis.
- **Arquitetura final desejada:** classificação por histórico real + pot family + posição + board/runout + SPR + sizing/action legality + hand/draw + adversário. Ter milhares de caminhos somente quando eles correspondem a estados realmente possíveis e têm políticas distintas; criar cobertura rastreável e fallback controlado, não apenas cartesian products. A etapa atual mantém 75 regras de ação e 10 helpers novos em OpenPPL, sem alegar completude.

**Métrica da HIST-v3 (ADR-027):** das 484 sequências legais flop→turn, a fonte OPPL v3 classifica **100** somente sob modelo documental de memória perfeitamente capturada; **384** não entram no domínio (264 flop/120 turn). Esse indicador, mais a taxa de replay real sem fallback, passa a orientar a expansão funcional. O próximo módulo precisa aumentar cobertura observável e associar ações em estados estratégicos, não apenas adicionar helper sem consumidor.

## Contrato mínimo do produto final: SUPERAR DeepCrusher_R10d (20/11/2026)
A comparação é com o [artefato R10d exato](https://github.com/pmartins87/DeepCrusher/blob/main/artifacts/r10/DeepCrusher_R10d_TBP_HARDENING_20261001.txt), não com um resumo. Seu inventário foi medido: 725 funções, 545 handlists, 6.021 WHEN, 1.561 comandos Set e 561 símbolos user_. O Heuristic6max mais recente, com 3bet HU, tem 88 funções, 187 handlists, 649 WHEN, 57 Set e 6 símbolos user_ próprios. **Há um gap substancial; não alegar completude/superioridade.** Completude é dominância funcional, não contagem bruta; melhorar além de R10d significa incluir todas as 14 famílias auditadas em [CAPABILITY_MATRIX.csv](benchmarks/r10d_floor/CAPABILITY_MATRIX.csv) e extensão significativa como multiway 4–6 players.
- Executável mais recente em DRAFT: [preflop + SRP-HIST-v3 + 3bet HU](portability/p3bet_hu_v1/preflop_srp_and_3bet_hu_draft.oppl); 39 regras novas de 3bet HU e captura de intenção, não execução.
- Engenharia orientada por gargalos: história real de ações e classificação do pote → cobertura de famílias faltantes → política por board/SPR/oponente → validação prática → promoção. Não usar multiplicações cartesianas de cenários como se fossem decisões.
- Release bloqueado até `PROMOTION_GATE.json` com evidência real, verificação de histórico/fallback/legalidade e cobertura comparativa. G2-a segue HOLD para alterações estratégicas, mas adições em novas famílias são DRAFT sob revisão.

## SRP 3-way e evolução do mínimo R10d
- Adicionado [módulo p3way_srp_v1](portability/p3way_srp_v1/README.md): 31 novas ações pós-flop para Hero PFR ou caller VS_OPEN, 33 comandos `Set` derivados da estratégia original, nativos de verificação do call/raise.
- O arquivo combinado [preflop_srp_3bet_3way_draft.oppl](portability/p3way_srp_v1/preflop_srp_3bet_3way_draft.oppl) soma 729 WHEN, 92 funções, 187 listas, 90 registros Set, 7 símbolos user_. **Ainda muito inferior em amplitude ao R10d**; a meta não pode ser substituída por mais 31 regras superficiais.
- Ponto de decisão: próximo aumento de abrangência deve resolver estados relevantes ausentes (multiway que vira HU, potes 3bet multiway e 4–6 players, limp/iso e 4bet), não inflar o grafo de históricos sem políticas. Avaliação futura exige ação final OpenHoldem e cobertura de cenários reais.
