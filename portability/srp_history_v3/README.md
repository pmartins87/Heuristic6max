# G3 — HIST-v3: histórico cronológico, aliases e memória OpenPPL

**20/11/2026 — módulo DRAFT do bot completo Heuristic6max. NÃO É BOT OPERACIONAL.**

## Por que 36 não eram suficientes

A HIST-v2 enumerava 6 x 6 **classes resumidas** de flop/turn, e não trajetórias cronológicas individuais. Além de colapsar reraise/4bet e posição, usava `OpponentCalledOnFlop/Turn` de forma incompatível com a definição na biblioteca OpenPPL pública (quando o vilão apostou previamente). Por isso, rotas `RAISE_OVER_VILLAIN_BET_CALLED` e `CHECK_RAISE_CALLED` podiam ser **inalcançáveis** apesar de declaradas presentes. V2 permanece imutável por rastreabilidade; HIST-v3 corrige as invocações das regras no arquivo novo, sem reescrever as ações.

## O que foi realmente entregue

1. **484 trajetórias cronológicas distintas** que atravessam flop e turn e chegam ao river (`HIST3_484_CHRONOLOGICAL_PATHS.csv`). Cada street possui 11 **sequências legais completas** (check/check, bet/call, bet/raise/call, check/bet/call, check/bet/raise/call e cadeias de até quatro raises); há dois posicionamentos (Hero IP/OOP) e dois papéis PF (Hero agressor/caller): `11 × 11 × 2 × 2 = 484`.
2. Enumerador também representa linhas terminadas por fold: 10 por street/posição. **Elas não são confundidas com caminhos que chegam ao river.** Não modela all-ins, stacks, sizings, multiway, potes 3-bet ou 4-bet, nem tem política para as 484 linhas. **484 = casos de cobertura do modelo, NÃO regras estratégicas prontas nem nós validados no OpenHoldem**.
3. `HIST3_OBSERVABILITY.csv`: usando os flags do OpenPPL conforme código da biblioteca de referência, há **3 colisões por posição IP** entre sequências legais diferentes que produzem a mesma assinatura agregada; isso demonstra que um classificador só com flags não pode conhecer a ordem exata.
4. `hist3_gate_helpers.oppl`: **10 helpers OpenPPL** adicionais. Quatro substituem inferências de `RaiseCall` e `CheckRaiseCall` que dependiam de `OpponentCalledOnFlop/Turn` sem respeitar a biblioteca; dois exigem provenance para `BetRaisedCall` IP; dois promovem classificação apenas quando não há alias; dois criam domínios de turn/river mais restritos.
5. `history_memory_capture.oppl`: **4 sentenças `Set user_...`** observacionais (2 flop, 2 turn) que marcam se o bot já havia apostado ou aumentado antes de enfrentar um raise adversário. Capturam apenas um evento **anterior identificado por `BotsLastFlopAction`/`BotsLastTurnAction`**, não presumem que a decisão corrente tenha sido executada. O estado é por mão, mas OpenHoldem pode reiniciá-lo após falha de scraping/oclusão.
6. `srp_hu_history_v3.oppl` e `preflop_srp_history_v3.oppl`: arquivo de regras HIST-v2 com **mesmas 75 ações pós-flop**; o novo roteamento é mais seguro e quatro capturas de memória acontecem antes das regras. Pré-flop RFI + VS_OPEN + VS_3BET preservado **byte a byte**. Nenhum range nem sizing alterado.
7. `history_v3_interpreter.py`: intérprete offline estrito das linhas do mesmo OPPL, com `Set` side-effect, testes de histórico, prioridade e guardas — não é segundo algoritmo de pôquer. `test_history_v3.py`: **31 testes** novos; gera outputs determinísticos.

## Exemplo de colisão — ambos eram classificados da mesma forma

- `V:B H:R V:R H:C` = adversário aposta; Hero dá raise; adversário dá reraise; Hero paga.
- `V:X H:B V:R H:C` = adversário faz check; Hero aposta; adversário dá raise; Hero paga.

O Hero está IP nos dois casos. Flags agregados de raise/call e número de raises do vilão não informam quem **iniciou** a aposta. O segundo deve ser tratado como `bet-raised-call`; o primeiro não. HIST-v3 exige memória observacional `user_H3_IP_FlopLeadBetFacedRaise` para aplicar as regras da segunda linha. Sem essa memória, não classifica o contexto como seguro.

## Regras de segurança e escopo

- A fonte é **OpenPPL**. Python é apenas gerador/gramática de cenários e intérprete de teste.
- `OpponentsOnFlop = 1`, SRP, HU e todas as guardas da versão anterior continuam; as flags OPPL precisam ser confirmadas na instalação real do OpenHoldem.
- Nenhuma equivalência operacional foi demonstrada. O arquivo de regras resultante ainda pode cair em `default.bot` quando não houver `WHEN` correspondente; o teste Python retornar `None` **não** equivale a fail-closed em OH.
- Este checkpoint **não concede 484 decisões estratégicas**, nem prova excelência GTO. A próxima expansão depende de inserir mecanismos de sequência resolvida e política de ação para cada linha realmente alcançável, por posição, textura, SPR, sizing e família de pote.
- Não alterar RFI/VS_OPEN/VS_3BET, nem HIST-v1/v2, só para melhorar contagens.

## Testes

Da raiz do repositório:

```sh
python -m unittest discover -s portability/srp_history_v3 -p 'test_*.py' -q
python portability/srp_history_v3/build_history_v3.py
git diff --exit-code -- portability/srp_history_v3/HIST3_484_CHRONOLOGICAL_PATHS.csv portability/srp_history_v3/HIST3_OBSERVABILITY.csv portability/srp_history_v3/srp_hu_history_v3.oppl portability/srp_history_v3/preflop_srp_history_v3.oppl
(cd portability/srp_history_v3 && sha256sum -c HIST3_SHA256SUMS.txt)
```

**Total CI esperado após incluir o módulo: 344 (313 anteriores + 31).** A CI é verificação estática, nunca certificado de jogabilidade/EV.

## Referências inspecionadas e uso permitido

- Material exato do projeto: `DeepCrusher_R10(1).txt` (mais de 20 mil linhas, notas históricas e implementação OpenPPL). Não foi copiado como estratégia Heuristic6max.
- [DeepCrusher R10d — auditoria](https://github.com/pmartins87/DeepCrusher/blob/main/docs/audits/R10D_TBP_HARDENING_20261001.md) e [política de validação](https://github.com/pmartins87/DeepCrusher/blob/main/docs/strategy/DEEPCRUSHER_SOURCE_FIRST_E2E_POLICY.md). O R10d tem **1.271 cabeçalhos** reportados; a política documenta 331 contratos pós-flop históricos do ciclo R8. **Nem cabeçalhos nem contratos equivalem diretamente a número de trajetórias.**
- [Biblioteca OpenPPL de Betting Action Symbols](https://github.com/OpenHoldem/openholdembot/blob/master/OpenPPL/OpenPPL_Library/OpenPPL_Library_Betting_Action_Symbols.ohf) define `OpponentCalledOnFlop`/`OnTurn` condicionados a `NoVillainBetOrRaised...`, daí o defeito v2.
- [Manual OpenPPL, User-Defined Variables](https://documentation.help/OpenPPL/User_Defined_Variables.html): `Set user...` grava flag por mão e não executa um `FORCE`.
- [Betting-Action Symbols](https://github-wiki-see.page/m/OpenHoldem/openholdembot/wiki/bettingaction_symbols): `BotsLastFlopAction`/`BotsLastTurnAction`, caveat de counters por órbita estável.

## Caminho obrigatório para completar o bot

Após HIST-v3, conectar logs/replay reais (offline) que capturem cada evento antes de construir milhares de `WHEN` de decisão. Expandir para families SRP/HU (flop, turn, river), 3bet/4bet pots, limp/iso, multiway e conflitos de ação; separar textura, SPR, sizing e posições só quando exigirem decisões diferentes; medir cobertura de *estados alcançáveis* e taxa de ramo não reconhecido. Abrir gate de integração somente depois de controle do fallback e ação final, não por contagem de regras.
