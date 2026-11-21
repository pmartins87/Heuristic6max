# Revisão humana exigida para G1/G6 — NÃO preencher sem dados reais

A auditoria automática pode rejeitar material inconsistente, mas não pode autenticar o OpenHoldem. Para cada um dos 10 casos de `CASE_MATRIX.json`, registrar na pasta privada:

- **Ambiente:** versão exata de `OpenHoldem.exe`, hash SHA-256 do executável, origem/versionamento da biblioteca OpenPPL, hash e nome da tablemap, hash da fórmula carregada, captura do Formula Editor sem erro de parser. A versão/documentação de ~2015 **não** é prova da build instalada.
- **Antes da decisão:** dois arquivos replay `.html`/`.bmp` de mesmo stem, captura do `f$debug`, e todos os símbolos exigidos pelo caso. Comprovar se os valores de `Raises`, `Calls`, `StillToAct`, `FirstRaiserPosition`, `LastRaiserPosition` e `PotSize` correspondem à ação realmente ocorrida, não apenas à descrição do cenário.
- **Fórmula e intenção:** identificação da primeira regra OpenPPL correspondida, `Set user_*` (intenção), valor da ação `RaiseTo` ou call/fold/check em **BB**, e repetição estável em múltiplos heartbeats.
- **Autoplayer log:** segmento original com `Best action` e `Action taken` do mesmo timestamp. Se divergirem, classificar `FALLBACK_OBSERVED` e suspender promoção até investigar. `Action taken` pode representar tentativa de interação, NÃO necessariamente alteração aceita pela mesa.
- **Depois da decisão:** evidência independente do simulador *offline* que efetivamente reconheceu o comando e atualizou o pote/stack/currentbet. Um segundo frame estático sozinho é insuficiente. Se não existir receptor de ação funcional, marcar `FINAL_ACTION_UNPROVEN` e manter G6 PENDING.
- **Origem cronológica e reset:** comparar preflop → flop → turn → river e início de outra mão; memoria `user_*`, `BotRaisedBeforeFlop`, `BotCalledBeforeFlop`, `BotCheckedPreflop`, `NumberOfRaisesBeforeFlop` não devem vazar ou ser inferidas só de um frame. Verificar se ManualMode e OHReplay divergem; símbolos autoplayers podem estar indisponíveis em modo manual.
- **Controle negativo:** pelo menos uma observação fora do domínio e um conflito de scraping; não assumir que ausência de regra `WHEN` força `Fold`. Capturar efetivo `default.bot`/backup, se houver. No caso de instrução impossível, suspender.
- **Privacidade:** frames podem conter nickname, valores, título de janela e dados privados. Conservar originais localmente; antes de enviar para revisão, criar cópia expurgada e anotar SHA de ambas, sem publicar arquivos brutos no GitHub público.

## Estados formais do projeto

G1: **OPEN**. G2-a: **HOLD**. G6: **PENDING**. Piso R10d: **0/14 VERIFIED**.

Só recomendar mudança do estado mediante provas observadas, revisão crítica da compatibilidade na build alvo e atualização explícita de `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `HANDOFF.md`, `PORTABILITY_CONTRACT.md`, `RELEASE_MANIFEST.md` e do gate de release quando realmente justificável. Não modificar `PROMOTION_GATE.json` no presente checkpoint.
