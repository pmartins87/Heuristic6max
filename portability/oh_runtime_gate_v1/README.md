# OH-G1G6-1 — pacote de evidência real do OpenHoldem, OFFLINE

**Gate de validação, não motor de pôquer e NÃO release.** Base da `main`: ISODEF-1, `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`, 2.007 `WHEN`. Este pacote **não modifica uma única regra de ação** nem ranges v0.6.1, ISO-1, BLISO-2 ou ISODEF-1. Não compila, inicia, conecta, clica ou habilita o autoplayer. Sem dados de execução fornecidos pelo usuário, o resultado é somente **instrumentação e testes sintéticos**.

## Por que este gate existe

A documentação fornecida no anexo do projeto `OpenHoldem e OPPL Manuais e Library.zip` confirma:
- `OpenHoldem Manual.pdf`, seções **Log-Files / Basic Info**: há **Best action** (decisão calculada) e **Action taken** (ação tentada/executada pela camada de autoplayer), podendo ser diferentes por ação substituta. O exemplo oficial traz `Best action: f$call` e `Action taken: f$check`.
- Seções **Preferences – Logging**, **Replay Frames**, **OHReplay**, **Debug-Tab**: configurar Basic Info e Autoplayer Traces, `f$debug` e pares `.bmp` + `.html` de replay. A dupla BMP/HTML contém contexto da janela/cassino; **somente o BMP não basta**.
- `OpenPPL Manual.pdf`, seções **Working with the debug-tab**, **Simulating positions**, **Investigating log-files**: expressões `= Raises`, etc. são consultadas em `f$debug`; ManualMode e OHReplay são meios de reproduzir situações.
- `OpenPPL_Library_Integrated.txt`, funções `Calls`, `NumberOfRaisesBeforeFlop`, `BotRaisedBeforeFlop` e **GameStateChangedSinceLastAutoplayerAction**: contadores sofrem influência do ciclo de captura/heartbeat; o manual diferencia ações do autoplayer e ações manuais. Portanto capturar uma tela isolada NÃO prova resets, reentradas, `Set user_*` ou história cronológica.

Esses materiais são históricos (aprox. 2015), **não demonstram** que a build instalada do usuário tenha exatamente a mesma semântica. Especificar build + hashes é obrigatório.

## O que foi criado

- `CASE_MATRIX.json`: **10 cenários-gate**, da fonte OpenPPL ativa (RFI, VS_OPEN, VS_3BET, ISO, BLISO, ISODEF, transição multiway, no-match/fallback, nuts vs overbet e reset de memória). Cada cenário fixa os símbolos a inspecionar e verifica que o marcador ainda aparece no integrado. **Não fabrica cenários que já ocorreram**.
- `evidence_gate.py`: analisa cópias **privadas** de evidências, sem acesso à engine. Confere SHA-256 da fonte integrada, versão/hash exe e tablemap informados, artefatos (.html/.bmp, before/after, f$debug texto+imagem, trecho de log), sequência e `randomhand`, contadores transcritos e `Best action` versus `Action taken` no trecho de log. **Jamais escreve `runtime_approved=true`**, nem altera `PROMOTION_GATE.json`.
- `build_template.py` e `SYNTHETIC_BUNDLE.json`: modelo com SHA da fonte verdadeiro, mas **todos os campos de OH reais em branco** e rotulado `SYNTHETIC`. Não substituir por números imaginados.
- `collect_file_fingerprints.ps1`: somente `Get-FileHash SHA256` e versão do executável na **VM offline Windows**, sem abrir o OpenHoldem ou modificar configurações.
- `test_evidence_gate.py`: 26 testes de evidência (incluindo bytes e hashes inválidos, live-connection, false-pass, ação substituta, par temporal e estabilidade do `randomhand`), todos com **fixtures falsos explicitamente identificados**.
- `REVIEW_CHECKLIST.md`: procedimento humano de aceite e limitações.
- `OHG1G6_SHA256SUMS.txt`: integridade dos arquivos públicos. **Nunca adicionar** arquivos privados na pasta do projeto.

## Coleta no computador do usuário — SOMENTE offline, quando houver ambiente pronto

1. **Desligar e desconectar qualquer mesa com apostas.** Usar ManualMode (primeiro, apenas semântica de símbolos) ou OHReplay com frames já existentes, no ambiente isolado. Não carregar o bot em jogos reais. Identificar versão da aplicação OpenHoldem, DLL/biblioteca de símbolos, tablemap e fórmula efetivamente selecionada.
2. Executar no PowerShell **somente o coletor de hash** se necessário (caminhos devem ser ajustados):

   ```powershell
   .\collect_file_fingerprints.ps1 -OpenHoldemExe 'C:\OH\OpenHoldem.exe' -OpenPPLFormula 'C:\OH\iso_defense_integrated_draft.oppl' -TableMap 'C:\OH\maps\table.tm' -OutputJson 'C:\OH\evidence_private\fingerprints.json'
   ```

   O coletor **não prova** que o arquivo de fórmula com esse hash foi carregado; só identifica bytes locais. Validar no Formula Editor a seleção e eventuais erros de compilação.
3. Em `Preferences → Logging`, verificar **Basic Info** e **Autoplayer Traces**, sem habilitar execução de ações em mesas reais. Na tela de `Formula Editor → f$debug`, uma expressão por linha (prefixo `=`), coletar os campos da **CASE_MATRIX**, e salvar captura de tela e transcrição `symbol=value` (por exemplo `Raises=1`). Campos ilegíveis devem ficar ausentes, jamais ser estimados.
4. No modo **Replay Frames**, associar **`.html` e `.bmp` com o mesmo nome-base**, antes e depois da ação. `OHReplay.exe` abre o `.html` via F2/Ctrl+O e permite conectar o OpenHoldem ao replay offline. Guardar trecho correlacionado do `oh_NN.log` com apenas **uma** ocorrência de `Best action:` e **uma** de `Action taken:` com o mesmo timestamp. NÃO transcrever `Action taken` a partir de `Best action`.
5. Manter os arquivos em pasta **fora do repositório público**; usar na cópia do projeto a subpasta ignorada `portability/oh_runtime_gate_v1/private_evidence/`. Preencher uma cópia de `SYNTHETIC_BUNDLE.json`, mudando para `OH_REPLAY` ou `OH_MANUALMODE` **somente depois de capturar evidência autêntica**, e inserir hashes SHA-256 de cada arquivo. Os três hashes de executável/tablemap/fórmula devem ser conferidos.
6. Rodar **sem conectar software nenhum**:

   ```bash
   python portability/oh_runtime_gate_v1/evidence_gate.py --bundle portability/oh_runtime_gate_v1/private_evidence/bundle.json --evidence-root portability/oh_runtime_gate_v1/private_evidence --out portability/oh_runtime_gate_v1/private_evidence/report.json
   ```

   A leitura do relatório é **triagem**: `STATIC_ONLY`, `INCOMPLETE`, `SOURCE_MISMATCH`, `SYMBOL_CONFLICT`, `EVIDENCE_CONFLICT`, `FALLBACK_OBSERVED`, `OBSERVATION_ONLY`, `MISMATCH_RANDOM`, `BLOCKED_LIVE_CONTEXT` ou, no máximo, `READY_FOR_HUMAN_REVIEW`. Nenhum deles aprova G1/G6 automaticamente.

## Onde o gate para

Um par `Best action` / `Action taken` pode informar o **comando emitido pela camada de autoplayer**, mas não autentica, sozinho, aceitação pelo alvo nem alteração de fichas. Replay frames estáticos do OHReplay não são prova suficiente de uma ação efetivamente processada pelo jogo. Para fechar **G6** exige-se validação humana do contexto, trace completo, legalidade de sizing, estado posterior de simulador offline que efetivamente receba a ação, e ausência de fallback inesperado. Para fechar **G1** exige-se também estabilidade de contadores em múltiplos heartbeats e resets entre mãos, na versão alvo.

**Regras de parada:** sem `OpenHoldem.exe` e tablemap identificados + frames autênticos + log correlacionado e confirmação de ação no simulador, manter **G1 OPEN, G6 PENDING, G2-a HOLD, R10d 0/14 VERIFIED**. Retomar desenvolvimento de branches estratégicos somente depois de aprender com os resultados — não ampliar política às cegas.

## Reprodutibilidade local

```bash
python -m unittest discover -s portability/oh_runtime_gate_v1 -p 'test_*.py' -q
python portability/oh_runtime_gate_v1/build_template.py
git diff --exit-code -- portability/oh_runtime_gate_v1/SYNTHETIC_BUNDLE.json
(cd portability/oh_runtime_gate_v1 && sha256sum -c OHG1G6_SHA256SUMS.txt)
python portability/oh_runtime_gate_v1/evidence_gate.py --bundle portability/oh_runtime_gate_v1/SYNTHETIC_BUNDLE.json --evidence-root portability/oh_runtime_gate_v1
```

A última chamada deve retornar `STATIC_ONLY`, `runtime_approved=false` e `R10d_release=BLOCKED`.
