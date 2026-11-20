# PORT-2 — LJ RFI 169 classes, KJo 40/60 por `randomhand`

**2026-11-20 — APENAS PARIDADE ESTÁTICA, NÃO OPERACIONAL, NÃO CARREGAR NO OPENHOLDEM.**

## Decisão técnica

A sugestão conceitual de misturar ranges com condição randômica em OpenPPL foi incorporada pela via mais simples documentada, sem hash, sem memória ad hoc e sem alterar a estratégia histórica. O próprio arquivo `lj_rfi_mixed_port2.oppl` é a única fonte de regras para o interpretador de testes Python. O gerador offline lê a baseline v0.6.1 e gera estas regras, mas **a estratégia executável não depende de Python**.

A documentação fornecida descreve `randomhand` como símbolo de OpenHoldem no intervalo **[0,1)**, sorteado uma única vez por mão; logo:

```text
WHEN (GUARD ... AND listPORT2LJMIX AND randomhand < 0.40) RaiseTo 2.5 FORCE
WHEN (GUARD ... AND listPORT2LJMIX AND randomhand >= 0.40) Fold FORCE
```

A sintaxe acima resume as regras reais, que contêm guardas completas em cada `WHEN`. Na fonte `.oppl`, `listPORT2LJMIX` contém **somente KJo**; não inclui KJs. A faixa 0 ≤ `randomhand` < 0.40 gera raise nominal 40%, e 0.40 ≤ `randomhand` < 1 gera fold nominal 60%, estável em avaliações repetidas na mesma mão **se a implementação real do símbolo cumprir o manual**.

**Fonte documental local:** `OpenPPL Manual.pdf`, capítulo *Other Symbols* (Random vs randomround / randomhand) e capítulo *Handlists*; `OpenHoldem Manual.pdf`, seção *randomhand* (valor calculado uma vez por mão). Manuais fornecidos ao projeto descrevem software antigo; a versão instalada e comportamento concreto do OH-alvo não foram identificados.

## Resultados de cobertura

- RFI LJ 6-max / 100 BB **169/169 classes** mapeadas sem mudar as frequências: 43 RAISE puro, 125 FOLD puro, KJo com mix 40/60.
- O interpretador lê **as mesmas listas e as mesmas quatro linhas `WHEN` do texto OpenPPL**; não possui tabela de estratégia Python duplicada.
- A enumeração determinística de **10.000 valores** em [0,1) retorna 4.000 raises e 6.000 folds para KJo. Este teste verifica o limiar matemático, **não** a distribuição aleatória real do OpenHoldem.
- Testes: guardas, limites 0,40, chamadas repetidas, ausência de sorteio reavaliado, rejeição de `Random`, `randomround`, linhas inesperadas/fallback, cobertura das 169 mãos, regeneração determinística, preservação de fontes.
- O PORT-1 anterior (168 mãos puras, KJo bloqueado) permanece um artefato histórico; este não o reescreve.

## Riscos e gates ainda abertos

1. **Sem execução real no OpenHoldem.** A estabilidade por mão e a compilação/símbolos/ações precisam de replay/teste no motor-alvo.
2. `None` em Python representa exclusivamente **no-match no interpretador**; OpenHoldem pode executar fallback, inclusive em estados não reconhecidos. Não usar como política de segurança.
3. Qualidade de scraping, estabilidade do histórico, 95–105 BB, unidades e exatidão da ação final RaiseTo 2.5 ainda não foram demonstradas em OH.
4. A correlação entre decisões futuras que reutilizam `randomhand` deve ser tratada por nó ao ampliar a estratégia; aqui existe **um único nó misto** por mão.
5. **G1 continua aberto, G2-a estratégico HOLD, G2-b bloqueado e G6 pendente.** PORT-2 fecha apenas o bloqueio de **expressabilidade estática do mix KJo**, não a equivalência operacional.

## Reproduzir

A partir da raiz do GitHub:

```sh
python -m unittest discover -s portability/port2 -p 'test_*.py' -q
python portability/port2/generate_port2.py
git diff --exit-code -- portability/port2/lj_rfi_mixed_port2.oppl portability/port2/PORT2_LJ_169_MAPPING.csv
cd portability/port2 && sha256sum -c PORT2_SHA256SUMS.txt
```

Gerador só atua nos dois arquivos derivados desta pasta; não edita política RFI/VS_OPEN/VS_3BET nem snapshots anteriores.

**Próximo teste imprescindível para promoção:** construir um pacote de replays em OpenHoldem de versão especificada (ambiente de teste sem apostas) com KJo e `randomhand` próximos de 0.40, comparação do valor visto pelo motor, resultado final, estabilidade entre avaliações, e mapeamento de fallback/ações ilegais. Até lá, NÃO OPERACIONAL.
