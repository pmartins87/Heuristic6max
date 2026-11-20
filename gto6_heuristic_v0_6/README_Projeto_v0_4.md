# GTO Heuristic 6-Max — FONTE DE VERDADE v0.4

**Data:** 20/11/2026  
**Estado oficial:** G0 aprovado; G1 ABERTO; G2 PARCIAL/DRAFT; G3–G7 pendentes.  
**Objetivo:** estratégia heurística documentada de NLHE cash 6-max, próxima de princípios GTO, com cobertura incremental e regras verificáveis. **Não é solver e não reivindica equivalência de EV ou winrate.**

> **PROIBIDO USAR EM MESA:** ainda não existe bot OpenPPL operacional, captura confiável de estado real ou políticas pós-flop. `None` significa SEM POLÍTICA, nunca Fold/Check. Ranges ainda não aprovados estrategicamente.

## 1. Fonte de verdade e preservação

1. Esta versão continua exatamente a v0.3, sem pivô de estratégia. `CHANGELOG_v0_4.md`, esta fonte de verdade e o inventário de hashes devem ser atualizados em toda evolução.
2. `rfi_reference.py`, `vs_open_reference.py`, `action_ledger.py`, `scenario_contract.py`, `strict_observation.py`, `vs_open_bridge.py`, `RFI_100BB_169x5_DRAFT.csv` e `VS_OPEN_100BB_15x169_DRAFT.csv` continuam byte-a-byte idênticos à v0.3. O teste `test_preserve_v03.py` congela os hashes.
3. Pacote v0.3, v0.2 e v0.1 devem permanecer como checkpoints separados. Nenhum arquivo original de DeepCrusher/CrusherTBP/AoF foi alterado.
4. Este ZIP contém apenas códigos de estudo e relatórios; não inclui decisões de postflop nem fórmula executável no OpenHoldem.

## 2. Escopo operacional de estudo (restrito)

| Variável | Aceito | Rejeitado |
|---|---|---|
| Formato | 6-max NLHE cash; seis jogadores dealt | outros números de jogadores |
| Stacks | TODOS entre 95 e 105 BB iniciais | stacks desiguais fora da faixa, shorts |
| Blinds | 0,5/1 BB, sem ante | straddles, ante, blinds variáveis |
| RFI | LJ/HJ/CO/BTN 2,5 BB; SB 3 BB | demais sizings |
| 3-bet | sizing exato gerado pelo VS_OPEN v0.3 (8 BB IP/10,25 BB OOP/9,6 BB BB vs SB) | 3-bet de qualquer outro tamanho |
| Ação anterior | RFI seguido de exatamente UMA 3-bet e fold dos demais | callers, squeezes, limpers, 4-bet antes do Hero, cold 4-bet, shove |
| Turno do Hero | Hero é o **opener original** enfrentando a 3-bet | cold caller ou jogador não participante do RFI |
| Ações de resposta | 4-bet normal, Call, Fold | 4-bet shove, 5-bet, sidepots, pós-flop |
| Dados de entrada | ledger de eventos confirmados + observação completa e estável | leitura direta de screenshot/log sem prova |
| Rake e EV | ainda não calibrados | alegação de GTO exata, uso em dinheiro real |

### 2.1 A árvore de 15 posições

LJ vs (HJ, CO, BTN, SB, BB); HJ vs (CO, BTN, SB, BB); CO vs (BTN, SB, BB); BTN vs (SB, BB); SB vs BB. Cada par tem 169 classes de mãos, total **2.535 linhas**, com `RAISE_RFI` de origem, `Reachable`, frequências condicionais 4-bet/call/fold e tamanho da 4-bet. No total, **888** registros correspondem a classes que têm chance positiva de RFI em nossa estratégia-base; **1.647** são explicitamente `NOT_REACHABLE_FROM_RFI` e não emitem ação. Os números não são hands observadas e não representam oportunidades de jogo reais.

### 2.2 Coerência entre as streets e o range anterior

A decisão VS_3BET só é autorizada para classes que o RFI do próprio Hero poderia abrir. Se, por exemplo, LJ jamais abre 72o, a ação na árvore LJ vs HJ 3-bet fica `None`, não vira fold silencioso. Em classes parcialmente misturadas no RFI, a escolha de resposta é **condicional a ter ocorrido efetivamente um raise anterior**. O estado e a sequência de ações são preservados no ledger.

### 2.3 Tamanho da 4-bet, nunca shove automático

O sizing é **raise-to** (contribuição total na street, não valor adicional), igual a `2,30 × 3bet-to` quando o opener será IP, ou `2,65 × 3bet-to` quando ele será OOP, arredondado a centésimos de BB. É uma aproximação heurística sem rake ajustado. Exemplo: LJ abre 2,5 BB; HJ aumenta para 8 BB; LJ pode elevar para **21,20 BB**, não 100 BB. BTN abre 2,5 BB; BB aumenta para 10,25 BB; BTN pode elevar para **23,58 BB**. A legalidade é verificada novamente contra o ledger.

### 2.4 Construção manual dos ranges

As classes de cada um dos 15 pares são descritas explicitamente em `vs_3bet_reference.py`, com grupos de 4-bet valor, 4-bet/call, 4-bet blefe/fold, call puro e call/fold. O código rejeita colisões entre grupos e classes que não existam no range RFI do opener. Frequências são hipóteses heurísticas: **nenhum solver foi executado**.

Os percentuais de defesa no CSV são **condicionados ao range de open original** e ponderados pelo número de combinações (6 pares, 4 suited, 12 offsuit). Eles **não** representam percentuais sobre todas as cartas iniciais, nem resultado ponderado pela chance de a mão enfrentar a 3-bet do adversário. Este último ponto exigirá modelar ranges adversários e blockers concretos.

## 3. Auditoria estratégica: HOLD (não aprovada)

O relatório `G2_VS3_Benchmark_Crosscheck.csv` compara os 15 nós com estatísticas **agregadas públicas** do ART/GTO 100 BB. Esse é um **teste de plausibilidade**, não reuso de ranges do solver nem evidência de que nossas árvores sejam equivalentes: rake, árvore de tamanhos, composição de ranges, suposições, posições e percentuais condicionais podem diferir. Materiais são usados somente como referências e em conformidade com condições de estudo pessoal.

### 3.1 Alarmes do comparativo

- **8/15 nós = `MAJOR_REVIEW`**: pelo menos uma ação difere mais de 8 pontos percentuais do comparador.
- **4/15 nós = `REVIEW`**: maior diferença entre 4 e 8 p.p.
- **3/15 nós = `CROSSCHECK_ONLY`**: nenhuma diferença superior a 4 p.p. no agregado. Isso **não equivale a aprovação**.
- Exemplo de desvio: CO vs BTN 3-bet prevê **8,9% 4-bet / 20,9% call / 70,2% fold**; agregado público do ART/GTO indica **18,9% / 16,1% / 65,0%**. A composição de 4-bet exige auditoria e possível revisão, não ajuste automático para igualar agregado.
- LJ vs HJ: nosso 4-bet **12,2%**, versus referência **21,3%**. SB vs BB: nosso 4-bet **7,8%**, versus referência **20,6%**, mas a referência também usa composição e frequência de RFI distintas.

**Decisão técnica:** manter o G2 aberto, marcar `STRATEGIC_REVIEW_REQUIRED`; não publicar nem portar esta política para OpenPPL até revisar os nós críticos e a matriz de mãos.

**URLs das fontes de comparativo** (todas agregadas, acessadas 20/11/2026):
- https://artgto.com/learn/ranges/utg/
- https://artgto.com/learn/ranges/mp/
- https://artgto.com/learn/ranges/co/
- https://artgto.com/learn/ranges/bu/
- https://artgto.com/learn/ranges/sb/

## 4. Testes e métricas

**114 testes automáticos aprovados**, anteriormente 91 na v0.3. Incluem:
- 15 confrontos × 169 classes (2.535 verificações de grade de estado/política), probabilidades, consistência com RFI, mãos premium e sizes legais;
- rejeição de squeeze, 3-bet fora do sizing, limper, cold caller, 3-bet all-in, outro stack, quarto aumento, hand inválida e snapshot inconsistente;
- invariância dos bytes de oito arquivos da v0.3;
- todos os testes preexistentes de G0/G1/RFI/VS_OPEN.

Todos os replays utilizados para estes testes são **sintéticos**, não logs de OpenHoldem. A execução testa a infraestrutura e os contratos, **não** EV, lucratividade ou força estratégica.

Para reproduzir (Python 3.10+, apenas biblioteca padrão):

```sh
cd gto6_heuristic_v0_4
python -m unittest -q
python generate_v04_artifacts.py
python vs_3bet_reference.py
```

Conteúdo principal: `vs_3bet_reference.py`, `vs_3bet_bridge.py`, `test_vs_3bet_reference.py`, `test_preserve_v03.py`, `VS_3BET_100BB_15x169_DRAFT.csv`, `G2_VS3_Benchmark_Crosscheck.csv`, `G2_VS3_Audit_Summary.csv`, `G2_Nodes_Inventory.csv`, relatório de testes e checksums. A documentação e os fontes v0.3 permanecem no mesmo pacote.

## 5. Roadmap vivo e critérios de decisão

| Gate | Estado | Critério de fechamento |
|---|---|---|
| G0 Arquitetura | APROVADO | preservado |
| G1 Ledger/observação/replay | ABERTO | replays reais verificados e validação de falha fechada, blinds/sidepot e discrepâncias quantificadas |
| G2 Ranges pré-flop | PARCIAL / HOLD | auditoria de RFI/VS_OPEN/VS_3BET, sizings/rake, VS_4BET/5BET, squeezes, cold actions, limps, diversos stacks e testes |
| G3 Pós-flop SRP HU | PENDENTE | árvores contextualizadas completas |
| G4 Pós-flop 3bet/4bet/limped | PENDENTE | árvores e sizings próprios |
| G5 Pós-flop multiway | PENDENTE | modelagem própria de jogadores extras |
| G6 OpenPPL/OH | PENDENTE | integração, replay, rollback e validação de símbolo/ação final |
| G7 Avaliação de estratégia | PENDENTE | regressão, métricas e stop rules |

### Próxima decisão recomendada

**Prioridade G2-a:** auditar manualmente os 8 `MAJOR_REVIEW` na matriz por classes antes de transformar VS_3BET em referência aprovada. Depois, G2-b: **VS_4BET**, conservando a mesma infraestrutura. O G1 seguirá aberto até evidência real, sem impedir testes isolados do G2. Não iniciar pós-flop enquanto G2 continuar em revisão.

**Critérios de parada:** divergência de pote/saldo, origem do estado incerta, política sem antecedente coerente, agressão ilegal, frequências não justificadas e discrepâncias estratégicas importantes sem revisão. `None` jamais se transforma automaticamente em Check/Fold.

**Ação do usuário:** nenhuma instalação ou coleta imediata. O pacote é apenas para estudo/arquivamento. Quando houver replays de teste sem dinheiro real, eles poderão ser usados no G1. Para prosseguir no desenvolvimento, solicitar continuação da revisão estratégica.
