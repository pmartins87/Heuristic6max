# PORT-1 parcial — RFI LJ 6-max, 100 BB, ações puras

**Data: 20/11/2026. PROVA DE PORTABILIDADE ESTÁTICA — NÃO OPERACIONAL.**

## Decisão: construir por texto OpenPPL único, não traduzir duas estratégias independentes

- `lj_rfi_pure_port1.oppl` é a fonte **estática** das duas decisões e duas handlists, escritas na sintaxe restrita OpenPPL; não é uma estratégia carregável em OpenHoldem. `port1_interpreter.py` lê as MESMAS listas e regras do `.oppl`, sem range estratégico Python paralelo.
- `generate_port1.py` é ferramenta OFFLINE de reconciliação com o **RFI v0.6.1 imutável**, não é parte do runtime de decisão; se a baseline mudar, a geração recusa prosseguir silenciosamente.
- `PORT1_LJ_169_MAPPING.csv` explicita todo o universo de 169 classes e a razão da classe excluída.
- `test_port1_lj_pure.py` contém 15 testes de correspondência exata com as 168 classes puras da baseline, guardas de contexto, sobreposições, recusas de sintaxe, regeneração determinística e integridade do código estratégico.
- `PORT1_SHA256SUMS.txt` valida os demais arquivos desta pasta.

## Cobertura efetiva — NÃO é o PORT-1 completo

| Condição | Resultado |
|---|---|
| Posição LJ (UTG em mesa 6-max), first-in, stacks 95–105 BB | Condições representadas no protótipo OpenPPL |
| 43 classes puras de RAISE | `RaiseTo 2.5 FORCE` |
| 125 classes puras de FOLD | `Fold FORCE` |
| **KJo** (RAISE 40%, FOLD 60%) | **NÃO MAPEADA**; não descartar a mistura |
| Qualquer outro cenário ou erro de observação | Sem regra no `.oppl`: **no-match não é falha segura** no OpenHoldem |

Observação: a guarda usa `IsPreflop`, `nplayersdealt = 6`, `InUTG`, `Raises`, `Calls`, `StillToAct`, `PotSize`, `AmountToCall`, `StackUnknown`, `StackSize`, `MinOpponentStackSize`, `MaxOpponentStackSize`. O manual OpenPPL fornecido (versão documental de 2015) descreve os símbolos ou seu uso em OpenHoldem. **Não foi testado se o OpenHoldem instalado pelo usuário reconhece e atualiza cada símbolo com o significado esperado em todos os ciclos.** Particularmente histórico de stacks, scrape, `PotSize` e controle de ordens devem ser verificados no runtime real.

**Não usar a saída `None` do interpretador Python como promessa de fail-closed em OH.** O motor OpenHoldem pode invocar outras funções, fallback e/ou adaptar apostas ilegais. Não executar a prova como bot, inclusive em mesas reais.

## Como reproduzir

Da raiz do repositório:

```sh
python -m unittest discover -s portability/port1 -p 'test_*.py' -q
python portability/port1/generate_port1.py
git diff --exit-code -- portability/port1/lj_rfi_pure_port1.oppl portability/port1/PORT1_LJ_169_MAPPING.csv
cd portability/port1 && sha256sum -c PORT1_SHA256SUMS.txt
```

A regeneração não é alteração estratégica: compara conteúdo derivado com baseline histórica. A pasta `gto6_heuristic_v0_6_1` continua intocada.

## O que é necessário para APROVAR o gate PORT-1

1. Definir e testar mecanismo de **mistura estável por nó** para KJo que realmente preserve o comportamento da política original, sem depender de `Random` novo a cada leitura.
2. Mapear qualidade/snapshot de scraping e o estado do histórico; confirmar todos os símbolos no OpenHoldem-alvo.
3. Verificar o comportamento de **não-correspondência e fallback** e controlar a ação final emitida (inclusive sizings ilegais/arredondamentos).
4. Comparar as decisões com a execução OpenPPL/OH real por *replay de teste sem apostas*, não apenas o nosso interpretador estático.
5. Só após esses pontos validar uma árvore RFI LJ completa; ainda não se deve avançar G6 nem chamar a estratégia GTO.

## Fonte documental

Manuais locais do projeto `OpenPPL Manual.pdf` e `OpenPPL_Library_Integrated.txt`, especialmente "Handlists", "Hand And Board Expressions", "Position Symbols", "Betsizes And Stacksizes" e "RaiseBy And RaiseTo Actions". Compilação/versão exata do OpenHoldem-alvo continua **desconhecida**.

**Próximo passo recomendado:** PORT-1b definir mecanismo seguro de mistura e sem fallback; em paralelo, G2-a estratégico permanece HOLD. Não completar este gate inventando uma política 100% pura para KJo.
