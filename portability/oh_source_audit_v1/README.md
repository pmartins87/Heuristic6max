# OH-SRC1 — revisão estática da semântica OpenHoldem/OpenPPL

**21/11/2026.** Entrega de engenharia independente da instalação particular do usuário. Para **desenvolver** o bot, NÃO é necessário hash de um `OpenHoldem.exe` local nem esperar frames ou logs reais. Essas evidências são necessárias **somente** para aferir o comportamento de um ambiente específico e validar a ação final, não para estudar a API de uma engine pública.

Este módulo audita `portability/iso_defense_v1/iso_defense_integrated_draft.oppl`, **sem modificar a estratégia**. Fonte de verdade continua `benchmarks/r10d_floor/CURRENT_GAP_REPORT.json`, `PROJECT_STATE.md`, `ROADMAP.md` e `DECISIONS.md`.

## Referências efetivamente consultadas (não substituídas por suposições)

- Anexo original do projeto **`repositorio_completo_openholdem.txt`**: código-fonte de `CSymbolEngineOpenPPLUserVariables.cpp` (método `UpdateOnHandreset`, limpa `_user_variables`), `CSymbolEngineCallers.cpp` (cálculo de `nopponentscalling` percorrendo apostas/jogadores e não uma simples gravação de evento limp), `CSymbolEngineRaisers.cpp` (varredura da primeira órbita) e `CSymbolEngineHistory.cpp`/autoplayer. Esses arquivos são **evidência de um snapshot fornecido**, não atestado da build instalada.
- Anexo **`OpenHoldem e OPPL Manuais e Library.zip`**, `OpenPPL_Library_Integrated.txt`: definições `##Calls##`, `##CallsBeforeOurFirstAction##`, `##Raises##`, `##NumberOfRaisesBeforeFlop##`, `##StillToAct##`, `##FirstRaiserPosition##`, `##LastRaiserPosition##` e `##BotRaisedBeforeFlop##`.
- Mesmo ZIP, **OpenPPL Manual.pdf**: `User-Defined Variables` (`Set user...` continua avaliando até encontrar uma ação; o flag é zerado no próximo hand reset); `Differences To Shanky And Old-Style-PPL` (ponto flutuante e operador aproximado `~~`); `Actions` (ajustes de sizing, backups).
- Fontes públicas independentes: [OpenHoldem/openholdembot](https://github.com/OpenHoldem/openholdembot), [biblioteca de símbolos de ação OpenPPL](https://github.com/OpenHoldem/openholdembot/blob/master/OpenPPL/OpenPPL_Library/OpenPPL_Library_Betting_Action_Symbols.ohf), [manual sobre comparação numérica](https://documentation.help/OpenPPL/Differences.html) e [fluxo de execução das regras](https://github-wiki-see.page/m/OpenHoldem/openholdembot/wiki/structure_of_a_ppl_file).

Os anexos completos **não foram copiados** para o repositório. Esta pasta versiona conclusões auditáveis e código que inspeciona o OpenPPL atual. O snapshot fornecido pode divergir do código atual upstream; qualquer divergência deve ser documentada antes de aplicá-la.

## Achados classificados

| ID | Evidência concreta | Implicação e decisão |
|---|---|---|
| **F1: igualdade exata de pote** | **436 de 2.007** linhas `WHEN` usam `PotSize = literal`; 15 valores distintos (202 vezes `4`, 54 vezes `12`, 10 vezes `7` etc.). O OpenPPL representa quantidades numéricas como reais; `7.0000000001 = 7` é falso | **Alerta de robustez**, não prova de falha prática. NÃO substituir globalmente por tolerância ou `~~`: isso mudaria os conjuntos de estados aceitos. Revisar cada domínio (incluindo BB, ISO, pós-3bet) antes de qualquer alteração intencional |
| **F2: Calls é derivado do estado e memória** | `Calls` consulta `CallsBeforeOurFirstAction` e `nopponentscalling`, ou valores anteriores da memória e `CallsSinceLastPlay`; o C++ verifica o valor atual da aposta por jogador | `Calls=1` não deve ser considerado automaticamente prova suficiente de que **houve exatamente um limp anterior ao raise** sem considerar posição/pote/histórico. Preservar os guardas adicionais; não criar squeeze amplo só com `Calls` |
| **F3: StillToAct tem restrição de órbita** | `StillToAct` usa `BotsActionsOnThisRoundIncludingChecks` e a fórmula de primeira órbita; depois tem ramo hint/0 | Uso permitido somente onde o Hero ainda não atuou. O ISODEF-1 possui guardas exatas e deve manter a restrição; não reutilizar `StillToAct` numa resposta a 4bet sem mapear a semântica |
| **F4: variáveis user_ resetam por mão** | `CSymbolEngineOpenPPLUserVariables::UpdateOnHandreset` executa `_user_variables.clear()` e manual confirma auto-reset | **Semântica de reset comprovada no código-fonte**. Incerteza residual é o *detector de handreset* na execução, não a ausência de implementação. Não bloquear a construção por falta de hash local |
| **F5: Set não é ação terminal** | Manual: quando `Set user_*` corresponde, engine marca `true` e **continua** até outra regra de ação. Duas origens atuais de defesa têm pares `Set`/RaiseTo e `Set`/Call com guarda idêntica | A auditoria mantém teste de identidade literal e ordem para 2×5 regras preflop; intenção não substitui prova da ação final |
| **F6: no-match não é Fold garantido** | Documentação descreve fallback/default e funções técnicas de backup; `None` num interpretador Python não tem semântica operacional assegurada | Continua obrigatória uma política explícita de ações legais/fallback e sua verificação antes de uma release, mas a fonte da estratégia pode continuar sendo desenvolvida independentemente |

### Outras contagens de risco, não KPIs de lucratividade

- `AmountToCall = 0`: **258** linhas (zero é uma condição estrutural útil).
- `AmountToCall = número não zero`: **400** linhas (sujeitas a análise de precisão contextual, não necessariamente incorretas).
- `StillToAct`: **103** linhas; `FirstRaiserPosition`: **343**.
- As classes de mão da v0.6.1, RFI/VS_OPEN/VS_3BET e políticas ISO/BLISO/ISODEF foram **preservadas**. Este relatório é um registro de *riscos e semântica*, não mais uma pontuação abstrata de testes.

## Como reproduzir a auditoria

```bash
python -m unittest discover -s portability/oh_source_audit_v1 -p 'test_*.py' -q
python portability/oh_source_audit_v1/audit.py --check
python portability/oh_source_audit_v1/audit.py     # Somente ao atualizar a fonte, seguido de revisão do diff
(cd portability/oh_source_audit_v1 && sha256sum -c OHSRC1_SHA256SUMS.txt)
```

`SOURCE_FINDINGS.json` é determinístico e derivado do OpenPPL integrado que consta no benchmark R10d; `audit.py --check` bloqueia snapshots obsoletos. Os testes **não executam o OpenHoldem** e não certificam EV.

## Estratégia de trabalho a partir deste achado

**Construção e documentação de fonte:** continuar sem hash privado; revisar significado dos símbolos e corrigir problemas demonstrados com testes. **Gate de release e teste de uma instalação específica:** continua distinto; não afirmar que uma versão desconhecida executa um perfil complexo com sucesso. No caso de F1, a decisão recomendada é introduzir uma abstração explícita e **precisa** de tolerância apenas após comparar suas colisões com outros contextos e o comportamento documentado do símbolo; mudança generalizada é tecnicamente pior do que o tratamento dirigido.

Nenhuma mudança em `PROMOTION_GATE.json`, nenhum relaxamento de G2-a. G1/G6 continuam pendentes para **certificação operacional**, mas não impedem pesquisa, auditoria, autoria source-first e evolução técnica do bot. **R10d: 0/14 capacidades integralmente verificadas.**
