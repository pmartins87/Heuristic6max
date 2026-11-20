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
