# PORT-3 / RPL-0 — contrato de evidência para replay OpenHoldem

**20/11/2026 — Pacote de instrumentação e auditoria, NÃO teste de runtime executado.**

Este checkpoint prepara a comparação entre a **fonte OpenPPL PORT-2**, a **decisão da fórmula OpenHoldem** e a **ação final executada**. **Não** injeta ações nem opera o OpenHoldem; testes rodam somente em Python. A baseline `gto6_heuristic_v0_6_1/`, os ranges e todos os snapshots anteriores permanecem inalterados.

## O que foi criado

- `replay_audit.py`: lê o CSV com observações e passa as mesmas entradas do motor ao interpretador da **fonte OpenPPL real** `portability/port2/lj_rfi_mixed_port2.oppl`, sem duplicar ranges. Compara decisão, tamanho do raise e ação final informada. Verifica repetição de `randomhand` por `(session_id, hand_id)`, rejeita fonte divergente, dados malformados, ordens duplicadas e evidencia que *no-match não é fail-closed*.
- `test_replay_audit.py`: **27 testes novos** (KJo nas duas faixas, 169 classes, repetição, diferentes mãos, fallbacks, tamanhos divergentes, origem, hashes, caminhos inseguros e saída determinística).
- `SYNTHETIC_REPLAY_INPUT.csv`: seis estados **explicitamente sintéticos**, com campos observados no OpenHoldem **vazios**. Nunca os apresentar como dados capturados.
- `SYNTHETIC_REPLAY_REPORT.csv`: saída reproduzível da auditoria: **5 STATIC_ONLY e 1 BLOCKED_NO_MATCH**, nenhum resultado de OH real.
- `PORT3_SHA256SUMS.txt`: manifesto dos outros arquivos do pacote.

A contagem acumulada esperada no CI é **242 = 215 + 27**. Passar nesses testes não significa aprovar PORT-3/G6.

## O que o manual respalda

- O OpenPPL possui o símbolo OH `randomhand` documentado em **[0,1)**, constante durante uma mão. Reaproveitar o mesmo valor permite checar KJo 40%/60% sem algoritmos próprios no runtime.
- O OpenHoldem oferece **ManualMode**, **OHReplay** e `f$debug` para investigar valores observados em replay offline; `oh_NN.log`/autoplayer log registra tanto decisão calculada quanto **ação efetivamente tomada**, que pode diferir por fallback ou legalidade.
- A versão e a semântica dos símbolos no executável **instalado** ainda não foram confirmadas. Esta camada não promete compatibilidade de um executável desconhecido.

**Fontes:** anexos do projeto `OpenPPL Manual.pdf` → *Other Symbols*, *Debugging Your Code*; `OpenHoldem Manual.pdf` → *Replay Frames*, *ManualMode*, *Logging*; documentação do projeto OpenHoldem em [Log Files](https://github-wiki-see.page/m/OpenHoldem/openholdembot/wiki/log_files) e [OHReplay](https://github-wiki-see.page/m/OpenHoldem/openholdembot/wiki/ohreplay).

## Formato exigido por replay de teste

O CSV de entrada possui **27 colunas obrigatórias**. Elas incluem:

1. **Identidade e origem:** `case_id`, `session_id`, `hand_id`, `eval_index`, `capture_source` (`SYNTHETIC`, `OH_MANUALMODE` ou `OH_REPLAY`), `openholdem_version`, SHA-256 da fonte `.oppl`.
2. **Valores observados:** classe, posição, blinds, contadores de ações, stack, `randomhand` e todos os guardas usados pelo PORT-2. Valores não lidos **não podem ser inventados**.
3. **Resultados do OpenHoldem:** `observed_formula_action`, `observed_formula_raise_to_bb`, `observed_final_action`, `observed_final_raise_to_bb` — são campos distintos; não preencher um a partir do outro.
4. **Evidência:** caminho de arquivo **relativo** ao diretório privado e respectivo SHA-256. Verificar checksum não demonstra que o arquivo veio de OpenHoldem; o log/frame ainda exige revisão independente.

**Status possíveis:** `STATIC_ONLY`, `BLOCKED_NO_MATCH`, `EVIDENCE_INCOMPLETE`, `MISMATCH_SOURCE`, `MISMATCH_RANDOM`, `MISMATCH_FORMULA`, `MISMATCH_FINAL`, `READY_FOR_MANUAL_REVIEW`. **Não existe `PASS`, `G6_APPROVED` nem aprovação de runtime automática.** Até `READY_FOR_MANUAL_REVIEW` significa apenas que os dados fornecidos são internamente coerentes e um arquivo com o digest esperado existe — *não autentica execução ou origem*.

### Como coletar prova REAL, futuramente, sem apostas

1. Identificar executável, build/versão e hash da fórmula carregada. **Desconectar qualquer mesa real**. Usar `ManualMode` ou `OHReplay` offline com replay frames de teste, sem stakes. Não acionar automações em mesa com dinheiro.
2. No `f$debug`, verificar separadamente `randomhand`, `InUTG`, `StillToAct`, `Raises`, `Calls`, `PotSize`, `AmountToCall`, stacks, `nplayersdealt` e eventuais guardas indefinidos. Guardar valores, frame e identificador da mão; observar múltiplos heartbeat/evaluation cycles.
3. Se houver emulação de ação offline, guardar o trecho de `oh_NN.log` referente **à mesma mão** com `Best action`/`Action taken` e o tamanho de aposta final. Se não houver ação final genuinamente observada, deixar o campo vazio e manter **EVIDENCE_INCOMPLETE**.
4. Repetir para KJo `randomhand` abaixo/acima de 0,40 (não manipular ou presumir quais valores vão sair), AA e 72o, boundary stacks 95/105, falhas de scraping e cenários fora da árvore. **Não inferir estabilidade por mão de uma única leitura.**
5. Redigir os registros necessários e comparar. **Nunca adicionar ao GitHub público frames/logs com dados de conta, mesa, jogadores ou cliente.** O diretório `private_evidence_not_tracked/` é ignorado pelo Git.

A prova de um bug (por exemplo, fórmula deseja RAISE mas OpenHoldem executa CALL, ou alteração de `randomhand` dentro da mesma mão) mantém o gate bloqueado. Não se deve resolver esse conflito ajustando o intérprete para fazê-lo concordar artificialmente.

## Reprodução totalmente offline agora

Na raiz do projeto:

```bash
python -m unittest discover -s portability/port3 -p 'test_*.py' -q
python portability/port3/replay_audit.py
# deve imprimir: 5 STATIC_ONLY, 1 BLOCKED_NO_MATCH; aprovação operacional ZERO

git diff --exit-code -- portability/port3/SYNTHETIC_REPLAY_REPORT.csv
(cd portability/port3 && sha256sum -c PORT3_SHA256SUMS.txt)
```

Para revisar observações genuínas **quando existirem**, manter CSV e logs privados, por exemplo:

```bash
python portability/port3/replay_audit.py --input /caminho/local/observacoes.csv --output /caminho/local/relatorio.csv --evidence-root /caminho/privado/logs
```

**Critério de parada:** preparar o contrato/replay e parar. NÃO avançar G6 apenas porque o auditor está verde. Antes de mudar qualquer range ou prometer equivalência operacional, exigir observações reais e revisão de `READY_FOR_MANUAL_REVIEW` por caso.
