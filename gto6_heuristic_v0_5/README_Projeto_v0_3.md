# GTO Heuristic 6-Max — FONTE DE VERDADE v0.3

**Atualização:** 20 de novembro de 2026  
**Estado:** G0 aprovado; G1 parcial; G2 parcialmente modelado **DRAFT**; G3–G7 pendentes.  
**Estratégia:** heurística de NLHE cash **6-max** inspirada em teoria GTO, **sem solver obrigatório**, sem garantia de EV, winrate ou equilíbrio.  
**NÃO EXECUTAR EM MESAS.** Não há bot jogável, ação automática, OpenPPL final, parser confiável de logs reais, validação de rake ou replay real do ambiente de destino.

## 1. Continuidade e fontes de verdade

- Baseline imutável: `GTO_Heuristic_6Max_v0.2_G1_G2_RFI_DRAFT.zip`, com 71 testes. Versões v0.1/v0.2 permanecem arquivadas e intocadas.
- `RFI_100BB_169x5_DRAFT.csv` v0.3 está **byte a byte idêntico** ao da v0.2. Não houve mudança furtiva em ranges RFI.
- `scenario_contract.py`, `strict_observation.py`, `rfi_reference.py` e `rfi_bridge.py` herdados. `action_ledger.py` recebeu só correção de atomicidade: shove ilegal não pode debitar fichas antes de erro.
- Este README e `CHANGELOG_v0_3.md` são obrigatórios em revisões futuras. Se o projeto passar ao GitHub, a cópia versionada deverá ser lida e atualizada a cada mudança, não esquecida no repositório.
- Os arquivos originais de **DeepCrusher**, **CrusherTBP**, **DeepKK** e projeto AoF não foram modificados.

## 2. Hipóteses e escopo exato v0.3

| Dimensão | Aplicação | Fora do escopo atual |
|---|---|---|
| Jogo | NLHE cash, exatamente **6 jogadores dealt** | 2–5-handed, MTT, Spin, AoF |
| Stacks | Todos os stacks iniciais entre **95 e 105 BB** | Outros stacks, assimetria grande |
| Blinds | **0,5/1 BB**, sem ante | Ante, straddle, múltiplos blinds |
| Open | **2,5 BB** de LJ/HJ/CO/BTN; **3 BB** de SB | Minraise 2x, 3x early, opens variados |
| Sequência | Exatamente um primeiro raise, sem limp, sem caller, sem 3-bet antes do Hero | ISO, overcall, squeeze, multiway, straddles |
| Ações disponíveis | `3BET`, `CALL`, `FOLD` | Reação a 3-bets/4-bets, all-in |
| Frequência mista | Hash determinístico por mão/nó | Reamostragem por screenshot |
| Rake | **Ainda desconhecido** | Validação de EV / afirmação GTO |
| Observação | Ledger de eventos confirmados + screenshot estável fornecido por outra fonte | Reconstrução automática a partir de log/scrape real |

SIZING: para o primeiro raise de 2,5 BB, estudo usa **3-bet para 8 BB em posição** ou **10,25 BB fora de posição**. Para open de 3 BB do SB, BB tem posição pós-flop e usa **3-bet para 9,6 BB**. São valores totais (`raise-to`) em BB, **não** `raise-by`. Não foram calibrados para rake/site específico.

**Correção importante:** open do SB para 3 BB já inclui a blind 0,5 BB. Com BB 1 BB, o pote observado é 4 BB, **não 4,5 BB**. Isso está codificado e protegido por testes.

## 3. Os 15 pares VS_OPEN (cada um contém 169 classes)

| Open | Defensores suportados |
|---|---|
| LJ (UTG) | HJ, CO, BTN, SB, BB |
| HJ | CO, BTN, SB, BB |
| CO | BTN, SB, BB |
| BTN | SB, BB |
| SB | BB |

Foram produzidas **2.535 linhas** (`VS_OPEN_100BB_15x169_DRAFT.csv`), com probabilidades que somam 100%, classes `AA`, `AKs`, `AKo` etc., tamanho de raise e proveniência. O componente RFI v0.2 preservado possui outras **845 linhas**, total **3.380 registros** nos dois conjuntos de estudo. Isso **não** equivale a cobertura total pré-flop.

### Como os ranges foram concebidos

Os 15 `Spec` de `vs_open_reference.py` incluem grupos **explícitos**:

1. `core`: 3-bet em 100% das combinações da classe.
2. `mix3c`: 3-bet parcial e call no restante (exceto SB, que converte o restante em fold).
3. `mix3f`: 3-bet parcial e fold no restante.
4. `call`: call puro.
5. `mixcf`: call/fold em frequência mista.
6. Classes não incluídas: fold puro.

A precedência é fixa `core > mix3c > mix3f > call > mixcf > fold`. **Sobreposições** entre grupos 3-bet são proibidas. O inventário `G2_Shadowed_Hand_Review.csv` registra casos em que uma mão listada em grupos de call também era coberta por grupo de 3-bet; prevalece o grupo 3-bet, sem somar frequências. A sobreposição exige revisão humana futura, mas não existe colisão silenciosa.

**Cuidado:** combinou-se conhecimento qualitativo de ranges (força, conectividade, posição e pot odds) com frequências iniciais **manualmente propostas**. Estas mãos individuais NÃO saíram de um solver; as taxas NÃO foram verificadas por EV. `DRAFT` significa que podem ser alteradas por evidência ou auditoria de confiabilidade.

### Comparação de agregados (não equivalência GTO)

Como controle de plausibilidade, `G2_Benchmark_Crosscheck.csv` contrasta o conjunto de defesa de BB com as taxas publicadas pelo Simple GTO (cash 6-max 100 BB na estrutura *500z*). Não compartilhamos necessariamente a mesma estrutura de rake. Os demais pares são comparados **apenas em 3-bet** com alguns agregados públicos do ART/GTO (modelo diferente e sem transposição de ranges individuais). **Comparar dois modelos distintos não prova equivalência.** Três casos estão marcados `REVIEW` (>3 p.p. de diferença na 3-bet do ART/GTO), e **não foram ajustados automaticamente** só para igualar percentuais.

Fontes públicas, para conferência, sem extração de conjuntos individuais:

- Simple GTO: https://simplegto.com/learn/preflop-statistics
- ART/GTO: https://artgto.com/learn/ranges/

### Exemplos de interpretação

- LJ abre 2,5 BB; BB enfrenta 1,5 BB a pagar. O conjunto BB vs LJ prevê 3-bet 5,76%, call 20,45%, fold 73,79% das 1.326 combinações. Referência externa 5,8% / 20,7% / 73,5%, mas isso não testa a seleção de mãos.
- BTN abre 2,5 BB; BB enfrenta 1,5 BB. O conjunto BB vs BTN prevê 3-bet 13,15%, call 31,61%, fold 55,23%.
- SB abre 3 BB; BB enfrenta 2 BB; pote 4 BB. O conjunto BB vs SB prevê 3-bet 15,78%, call 41,15%, fold 43,08%.
- Quando um jogador dá call entre o opener e o Hero, a árvore correta já não é `VS_OPEN` puro. `vs_open_bridge.py` retorna `None`, bloqueando decisão equivocada.
- Ao detectar open de 3 BB do LJ, ou stack de 80 BB, retorna `None` até existir política calibrada correspondente.

## 4. Arquitetura de decisão e segurança

```text
Fixture de ações verificadas/observação estável (NÃO é um parser OpenHoldem)
      -> evidence_ingest.py -> action_ledger.py
      -> strict_observation.py [reconcilia stacks, pote, turno, blinds, apostas]
      -> vs_open_bridge.py [verifica 6-max/100BB/open exato/sem caller]
      -> vs_open_reference.py [política DRAFT 3BET/CALL/FOLD]
      -> scenario_contract.py [normaliza pesos, sizing, hash estável]
      -> relatório de análise; nunca bot operacional
```

A camada de `strict_observation` recusa estados incompletos, mas **não garante** que os eventos foram capturados corretamente; a fonte que os coleta ainda não existe. `evidence_ingest.py` serve para importar **JSON de ações independentemente verificadas**; não converte log bruto de OpenHoldem e não torna dados sintéticos evidência real. Exemplos em testes são **sintéticos**.

### Bug corrigido

`action_ledger.py` agora verifica a possibilidade de aumento por `SHOVE` **antes** de mutar saldos. Se houver all-in parcial que não reabre a ação, tentar empurrar fichas para aumentar deve falhar e deixar o ledger intacto. Regressão específica adicionada.

## 5. Testes e reprodutibilidade

Requisitos: Python **3.10+**, biblioteca padrão. Extraia o ZIP e execute na pasta `gto6_heuristic_v0_3`:

```bash
python -m unittest -q
python generate_v03_artifacts.py
python vs_open_reference.py
```

Resultado desta versão: **91 testes passando**, inclusive 15 confrontos × 169 classes testados ponta a ponta contra **históricos e snapshots sintéticos coerentes**. A v0.2 tinha 71 testes. Os 20 novos testes ampliam a cobertura de contratos e não medem qualidade do pôquer.

Arquivos de exportação:

- `VS_OPEN_100BB_15x169_DRAFT.csv`: ranges VS_OPEN e sizings.
- `RFI_100BB_169x5_DRAFT.csv`: RFI herdado sem modificações.
- `G2_Nodes_Inventory.csv`: 5+15 nós disponíveis em DRAFT (sem deploy).
- `G2_Benchmark_Crosscheck.csv`: taxas previstas vs fontes de comparação; flags para revisão.
- `G2_Shadowed_Hand_Review.csv`: overlaps com prioridade intencional auditada.
- `TEST_REPORT_v0_3.txt`, `SHA256SUMS.txt`: evidência e inventário de integridade.

## 6. Roadmap, gates e condições de parada

| Gate | Escopo | Estado | Evidência necessária para fechar |
|---|---|---|---|
| G0 | arquitetura/contratos | **APROVADO** | preservado |
| G1 | captura, histórico, ações legais, imagem/board | **ABERTO** | replays reais de OpenHoldem 6-max com ações verificadas, snapshots completos, taxas de erros reportadas, edge cases de blinds/side pots e rejeição de incerteza |
| G2 | pré-flop completo | **PARCIAL** | RFI + VS_OPEN revisados e rakes, VS_3BET, VS_4BET, 5BET, overcall/squeeze/limp/shove, sizings e stacks parametrizados, testes finais |
| G3 | flop-turn-river SRP HU | PENDENTE | árvores por IP/OOP/board/hand/sizing/histórico |
| G4 | HU 3bet, 4bet, limped | PENDENTE | idem |
| G5 | multiway | PENDENTE | branches próprios |
| G6 | OpenPPL, integração OH | PENDENTE | logs reais, bot isolado, políticas sem overrides indevidos |
| G7 | desempenho e regressões | PENDENTE | métricas defensáveis e critérios de parada |

**Proxima sequência recomendada**: (a) auditoria de ranges marginais vs open; (b) construir famílias de resposta **VS_3BET** para opener/defensor com sizings de 100BB; (c) processar replays reais somente quando disponíveis, sem forçar o G1 a fechar. Não iniciar G3 antes de G2 aprovado.

**Critério de parada:** parar se contabilidade de pote/stack divergir, replay real não fechar, houver frequência sem racional ou decisão não coberta por perfil especificado. Nunca produzir `CHECK`/`FOLD` silenciosamente como substituto de política desconhecida.

**Ação necessária do usuário:** nenhuma para esta entrega. Só quando for conveniente, fornecer logs/replays verificados de mesa de teste 6-max (sem dinheiro real) para permitir avanço de G1. Por enquanto, solicitar a continuação da auditoria de G2 é suficiente.
