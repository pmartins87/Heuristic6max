# G3-HIST-v2 — 36 trajetórias históricas do pós-flop SRP HU

**20/11/2026 — incremento DRAFT do bot COMPLETO Heuristic6max.** Não é um solver, estudo científico ou módulo operacional certificado. A finalidade é criar milhares de caminhos coerentes com o histórico, posição, board e stacks ao longo do roadmap, preservando a origem **OpenPPL** das decisões.

## O que foi desenvolvido

- **Seis situações por street anterior**: `B`=bot apostou e adversário deu call; `C`=check-through; `X`=bot deu call à bet do vilão; `R`=bot deu raise sobre bet do vilão e recebeu call (sem check anterior); `H`=bot deu check-raise e recebeu call; `M`=bot apostou, sofreu raise e pagou. Os novos estados usam os símbolos documentados `BotCheckedOnFlop/Turn`, `BotRaisedOnFlop/Turn`, `BotCalledOnFlop/Turn`, `OpponentCalledOnFlop/Turn`, `NoVillainBetOrRaisedOnFlop/Turn` e `NumberOfRaisesOnFlop/Turn`.
- **36 trajetórias explícitas flop→turn**, cada uma com helper `f$HLPath2XX`. A matriz em `HISTORY_FLOP_TURN_36_PATHS.csv` associa os estados às funções OpenPPL. Uma trajetória só corresponde quando os flags descritos são coerentes; outras situações ficam sem classificação.
- **75 regras pós-flop** (`14 flop + 22 turn + 39 river`) e **70 funções**, dentro de `srp_hu_history_v2.oppl`, combinadas ao mesmo pré-flop original em `preflop_srp_history_v2.oppl`. Há 17 regras novas além das 58 do HIST-v1; as nove trajetórias anteriores preservam a mesma decisão sob os mesmos inputs.
- **18 testes novos** em `test_history_v2.py`: seis estados e 36 sequências exclusivas, preservação das nove trajetórias anteriores, prioridade das mãos fortes, históricos contraditórios, cobertura de nós ainda desconhecidos, integridade do código e estabilidade do mix. Total esperado **313 = 277 + 18 (HIST-v1) + 18 (HIST-v2)**.
- **Fonte:** `advanced_history_overlay.oppl` é escrita em OpenPPL. `build_history_v2.py` combina esse texto com o HIST-v1 preservado e gera somente os 36 helpers sintáticos da combinação de seis predicados já definidos. `history_v2_interpreter.py` apenas interpreta o mesmo arquivo, sem decisões Python paralelas.

## Comportamento novo por linha

- Check-raise feito pelo bot e pago no flop **não** é confundido com c-bet paga; no turn com top pair, predomina controle do pote. Draws fortes podem receber aposta de semiblefe seletiva via `randomhand`.
- Bet–raise–call no flop vira um histórico distinto; top pair isolado não gera automaticamente uma sequência de novas apostas e recebe resposta conservadora contra pressão posterior.
- No river, nove grupos historicamente relevantes têm regras particulares adicionais (por exemplo, após check-raise no flop e bet-call no turn), enquanto outros caminhos continuam com as decisões base de G3 condicionadas à **classificação V2**.

## Limites reais e critérios de segurança

1. A classificação de `R/H/M` é uma inferência de **flags agregados do OpenHoldem**; esses flags não são um log cronológico completo. Podem existir sequências diferentes com os mesmos flags, perda de atualização ou alternância de posições. A identidade da linha só será aprovada com replays no OH instalado, capturando ação final e histórico na mesma mão.
2. `NumberOfRaisesOnFlop/Turn` conta raises adversários; bets adversárias não contam. `BotRaisedOnFlop/Turn` engloba bet ou raise do bot. As guardas com `NoVillainBetOrRaised...`, `BotChecked...` e `OpponentCalled...` são **provisões**, não prova de reconstrução perfeita.
3. O código **não oferece linha para todos os contextos possíveis**: folds após raise, bet-call-raise múltiplos, limp/iso, squeeze, multiway, 3-bet/4-bet pots e perfis adversários continuam pendentes. `None` no simulador de testes NÃO representa um fallback seguro no OH; não executar o arquivo em mesas reais.
4. As ações são heurísticas candidatas, não output do solver; sua qualidade deve ser melhorada comparando mãos, ranges, replays, sizings, textura, SPR e tendências de oponentes. Quantidade de caminhos **não equivale automaticamente** a excelência estratégica.
5. Nenhuma modificação foi feita no baseline `gto6_heuristic_v0_6_1/`, no pré-flop ou nas versões HIST-v1 e G3 anteriores.

## Verificação reproduzível

A partir da raiz GitHub:

```bash
python portability/srp_history_v2/build_history_v2.py
python -m unittest discover -s portability/srp_history_v2 -p 'test_*.py' -q
git diff --exit-code -- portability/srp_history_v2/srp_hu_history_v2.oppl portability/srp_history_v2/preflop_srp_history_v2.oppl portability/srp_history_v2/HISTORY_FLOP_TURN_36_PATHS.csv
(cd portability/srp_history_v2 && sha256sum -c HISTORY_V2_SHA256SUMS.txt)
```

**Próximos gates úteis:** implementar histórico por ordem real de ações e posição (incluindo 2+ raises e ações intercaladas); segmentar as 36 trajetórias por textura de board, SPR e size bucket; desenvolver linhas específicas de 3-bet/4-bet pot, limp/iso e multiway; verificar consistência dos símbolos e `default.bot` no OpenHoldem real antes de declarar prontidão operacional.
