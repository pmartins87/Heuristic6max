# V2 F3-PILOT-01 — gate de evidência para OpenHoldem REAL, offline

**Data:** 21/11/2026. **Estado:** \`STATIC_SYMBOLIC_VERIFIED\` (modelo restrito), **não** \`OPENHOLDEM_VERIFIED\`. Não carregar em mesas reais. Subordinado a [Plano Vivo](../PLAN.md), [F2 profissional](../cases/BTN_BB_SRP_CBET_F2_PILOT.md) e [piloto OpenPPL](README.md).

## 1. Evidência técnica efetivamente obtida

Fonte nativa única: [f2_two_spots_draft.oppl](f2_two_spots_draft.oppl), SHA256 **af3636449f2bce7eea40bfc7f72e802f78aa35d8567e6632bed512c5957529af** e Git blob **b9775903bcb8d49c3fccae238c05f8e787bad4a6**. Essas identificações são da versão congelada para o piloto, e **não** podem ser aplicadas a uma fórmula modificada.

- [test_static.py](test_static.py): 4 testes estruturais.
- [strict_symbolic_replay.py](strict_symbolic_replay.py): interpreta **somente o subconjunto que existe no código atual**, com leitura das condições \`WHEN\`, precedência, \`Set user\`, chamada do helper, classes de cartas \`hand$\`/\`board$\` exatas e ações efetivas da mesma fonte. **Não** é o parser C++ OpenHoldem, não joga pôquer, não calcula EV.
- [test_adversarial.py](test_adversarial.py): **16 testes** adicionais, incluindo múltiplos subcasos; 20 testes totais passaram em Python local. Duas decisões-alvo, inversão na ordem física das cartas, preflop RFI para duas mãos de fixture, preço no flop, posição, nplayersdealt, ator BB, histórico, limites de stack, potes multiway, 3bet/limp, outras mãos/boards e streets sem política. Snapshot \`BEEP_NO_ACTION\` **é apenas interpretação estática de \`Beep FORCE\`**.

**Importante:** o modelo simbólico não inventa valores observados do motor. Assume que os símbolos de entrada foram lidos corretamente; \`HaveTrips\`, \`HaveTopPair\`, \`headsupchair\`, \`NumberOfRaisesBeforeFlop\`, \`BotRaisedBeforeFlop\` e \`user_V2PilotBTNOpen\` **ainda precisam ser conferidos no OpenHoldem instalado**. O código só restringe o **stack do Hero**, não prova stack efetivo do vilão; a referência 100 BB é um contexto de estudo, não um filtro operacional para ambos.

## 2. O que o manual e o fonte C++ do usuário apoiam

- **OpenPPL Manual**, *Hand And Board Expressions / Coding For Specific Suits*, e o código \`CSymbolEngineOpenPPLHandAndBoardExpression.cpp\`: os pares de cartas físicas com naipe (\`hand$QsJs\`, \`board$QhQc6d\`) são reconhecíveis; \`hand$QJs\` é ambíguo e pode gerar alerta de parsing.
- **OpenPPL Manual**, *User-Defined Variables*: \`Set user_...\` executa na condição verdadeira, segue avaliação até achar ação, e reinicia ao começo de cada mão.
- **OpenPPL Manual**, *Actions*: \`RaiseTo 2.5 FORCE\`, \`BetThirdPot FORCE\`, \`Check FORCE\` e \`Beep FORCE\` são ações/formatos documentados; \`Beep\` significa sinalizar **sem agir**, mas não demonstra que o autoplay real esteja seguro quando não há política completa.
- **OpenPPL Library Integrated**: \`NumberOfRaisesBeforeFlop\` pós-flop pode ler memória \`me_re_MemRaisesBeforeFlop\`, e \`NoBettingOnFlop\` considera bets do Hero. Exige teste com histórico real, **não** só snapshot de cartas.
- **OpenHoldem Manual**, *OpenPPL-Mode, ManualMode, Logging*: fórmula com \`f$preflop\` entra no modo OpenPPL; ManualMode simula estados offline; logging distingue **Best action** da **Action taken**; replay frames podem ser inspecionados posteriormente.

Os manuais fornecidos são históricos (OpenPPL 2015). **Não** presumir identidade com versão OH instalada sem conferir o build.

## 3. Sequência mínima de replay sem dinheiro, quando o executável estiver disponível

1. Desconectar o OpenHoldem de qualquer mesa com apostas. Abrir **ManualMode** (ou OHReplay com frames genuinamente coerentes), carregar tablemap para ManualMode e o arquivo \`f2_two_spots_draft.oppl\` pelo OpenHoldem em modo OpenPPL. Registrar versão/build do exe, hash SHA256 real da fórmula e qualquer parse/unknown-symbol warning.
2. Simular **do início da mão**, seis jogadores inicialmente dealt, BTN Hero, blinds 0,5/1, stacks de 100 BB para Hero e BB; sem limpers. Caso \`QsJs\`: obter RFI 2,5 BB **pelo motor**, SB fold, BB call, transição de street, BB check; só então avaliar \`Qh Qc 6d\`. Repetir separadamente \`Ah5h\` e \`As 7d 3c\`. Simplesmente injetar um flop sem a sequência pré-flop não prova os símbolos de histórico.
3. Na ferramenta de debug, capturar \`nplayersdealt\`, \`InButton\`, \`Position\`, \`OpponentsOnFlop\`, \`OpponentsLeft\`, \`headsupchair\`, \`bigblindchair\`, \`user_V2PilotBTNOpen\`, \`BotRaisedBeforeFlop\`, \`NumberOfRaisesBeforeFlop\`, \`NoBettingOnFlop\`, \`AmountToCall\`, \`StackSize\`, \`HaveTrips\`, \`HaveTopPair\` e o resultado de \`f$V2PilotBTNOpenRFIContext\`. **Não** preencher valores que não foram observados.
4. Para cada caso, registrar separadamente \`Best action\`, valor da bet no pot, \`Action taken\` e resultado de aceitação. Esperado: \`QsJs/QQ6r = BetThirdPot (~33,33% do pote)\`; \`Ah5h/A73r = Check\`. Conferir que 2,5 BB é o **total** do open e que o pot bruto após BTN 2,5 + BB 2,5 + SB 0,5 = 5,5 BB.
5. Controles negativos em **frames de laboratório**: altere uma variável por vez: mão, board, BB bet em vez de check, BB 3bet pré-flop, SB call, 5 jogadores, outra posição, estado \`user_\` falso e mão seguinte. Em cada controle, **nenhuma ação de aposta da V2 deve ser selecionada**. Um \`Beep\` ou \`NoMatch\` não demonstra que não houve ação automática: verificar log de ação final.
6. Preservar logs e frames em diretório privado fora do repositório; remover dados de conta/cliente antes de compartilhar qualquer recorte. Não publicar logs de mesa real. Idealmente anexar tabela de evidências com colunas: \`case_id,session_id,hand_id,openholdem_version,oppl_sha256,observed_state,expected_formula_action,observed_formula_action,observed_final_action,observed_final_amount_bb,trace_file_sha256,review_status\`.

## 4. Gates objetivos — não promover por testes autorreferenciais

| Evidência | Requisito | Estado |
|---|---|---|
| Fonte OpenPPL e dois spots | Identidade, prioridade, carta física e ações | **STATIC_SYMBOLIC_VERIFIED** apenas |
| Parsing OpenHoldem nativo | 0 erros de parsing/unknown symbol na versão-alvo | **MISSING** |
| Memória e histórico | RFI verdadeiro, Hero BTN, BB único, reset ao mudar mão | **MISSING** |
| Ação calculada vs tomada | 2 positivos, negativos e sizing BB/pote corretos | **MISSING** |
| Sem fallback inesperado | Nenhuma ação real por \`Beep\`/no-match | **MISSING** |
| Entrega de estratégia | Família de flops e ranges completos, execução e benchmark | **NOT READY** |

**Stop imediato:** parser rejeita expressões, simbolização incorreta de mão, marcador \`user_\` inconsistente, bet final diferente, ação fora do domínio ou impossibilidade de construir um histórico real em ManualMode. Nesse caso corrigir **somente** o problema demonstrado; não inventar estratégia ou desligar validações para obter verde.

## 5. Comandos reproduzíveis sem jogo e próxima dependência

Na raiz do repositório:
\`\`\`bash
python -m unittest discover -s v2/pilot_01 -p 'test_*.py' -v
\`\`\`

Próxima dependência externa: **OpenHoldem real no Windows com ManualMode/OHReplay e logs de testes offline**. Sem ela, F3 permanece **STATIC_SYMBOLIC_VERIFIED / OH_PENDING** e F4 fica bloqueado, por mais testes Python que passem. O projeto pode continuar pesquisa/arquitetura em outras famílias sem alegar runtime.
