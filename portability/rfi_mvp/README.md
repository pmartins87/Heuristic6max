# RFI-MVP — módulo OpenPPL first-in de cash 6-max (LJ/HJ/CO/BTN/SB)

**20/11/2026 | Entrega funcional de fonte estratégica, NÃO um bot completo.** Objetivo: construir um bot **heurístico aproximadamente GTO**, sem solver próprio, trabalho científico ou exigência de provar EV de cada ramo. O programa está em OpenPPL e não requer tradução manual de Python para uma segunda estratégia.

## Escopo implementado

- 845 pares (5 posições × 169 classes) em **21 regras OpenPPL** e handlists separadas sem sobreposição dentro de cada posição, todos gerados diretamente da baseline histórica v0.6.1.
- RFI em mesa 6-handed, 95–105 BB, primeiro a agir voluntariamente (`Raises = Calls = 0`), blinds 0,5/1 BB, pote de abertura 1,5 BB, tamanho de abertura de 2,5 BB LJ–BTN e 3 BB SB.
- **5 mixagens nativas por `randomhand`**, com limiares complementares `<` e `>=`: LJ KJo raise 40/fold 60; HJ QJo raise 50/fold 50; BTN 53s raise 50/fold 50; SB K3s raise 50/fold 50; SB 97o **limp (Call)** 75/fold 25.
- Outras 840 decisões puras representadas em listas: raise, fold e, na SB, limp.
- O arquivo `rfi_6max_mvp.oppl` é a **fonte única das decisões**. `rfi_source_interpreter.py` lê as regras desse arquivo; `generate_rfi_mvp.py` é ferramenta **offline** de publicação da política RFI v0.6.1, não parte do runtime.
- `RFI_6MAX_845_MAPPING.csv` é um índice para comparar posição, mão, ações e frequências, não uma estratégia alternativa.

### Frequências de abertura preservadas (conjunto de combinações físicas)

| Posição | RAISE | LIMP | FOLD |
|---|---:|---:|---:|
| LJ | 18,311% | 0% | 81,689% |
| HJ | 22,926% | 0% | 77,074% |
| CO | 29,713% | 0% | 70,287% |
| BTN | 43,741% | 0% | 56,259% |
| SB | 36,199% | 14,555% | 49,246% |

A tabela é da **heurística própria já definida**, não frequências que um solver teria aprovado no rake e sizing do usuário.

## Símbolos e correspondências importantes

- O manual OpenPPL fornecido mapeia 6-max a `InUTG` (LJ), `InMiddlePosition3` (HJ), `InCutOff` (CO), `InButton` (BTN) e `InSmallBlind` (SB). As quantidades respectivas de `StillToAct` são 5, 4, 3, 2 e 1 antes de qualquer ação voluntária.
- Para SB, completar o blind é `Call FORCE` com `AmountToCall = 0.5`; **não** é `RaiseTo 3` e não pode ser substituído por fold.
- Os guards e a interpretação `RaiseTo` em BB são hipóteses verificáveis pelo OpenHoldem-alvo. `randomhand` é constante por mão na documentação, mas faltam observações reais do executável do usuário.

## Testes úteis, sem burocracia de solver

```sh
python -m unittest discover -s portability/rfi_mvp -p 'test_*.py' -q
python portability/rfi_mvp/generate_rfi_mvp.py
git diff --exit-code -- portability/rfi_mvp/rfi_6max_mvp.oppl portability/rfi_mvp/RFI_6MAX_845_MAPPING.csv
(cd portability/rfi_mvp && sha256sum -c RFI_MVP_SHA256SUMS.txt)
```

**12 testes incrementais** incluem os 845 nós, os 5 mixes em limites, o limp SB, guardas de domínio, ausência de fallback disfarçado, integridade da baseline e reprodução do arquivo OPPL/CSV. A CI tem **254 testes esperados** (242 históricos + 12).

## Não está pronto para operar

Este arquivo cobre **somente abertura first-in**. Ainda faltam BB check/defesa, VS_OPEN, VS_3BET, squeeze, 4bet, pós-flop e tratamento inequívoco de cenários sem regra. **No-match na engine OpenHoldem pode cair em `default.bot`**, diferente de `None` retornado pelo intérprete de teste. Não carregar esta prova em mesa com apostas; tampouco afirmar que haja correção GTO ou winrate comprovado.

O próximo passo de engenharia é **gerar VS_OPEN a partir da estratégia existente**, reutilizando as funções de OpenPPL e registrando a origem das misturas sem reescrita em Python. A integração final OH (G6) continua bloqueada até replay real de teste e um fallback controlado. Não iniciar G2-b/VS_4BET antes de revisar G2-a; não abandonar código, ranges ou contratos históricos.
