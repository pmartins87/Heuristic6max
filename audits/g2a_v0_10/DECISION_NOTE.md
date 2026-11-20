# ADR-014 — equity bruta por mão não autoriza mudanças na defesa de 3-bet

**20/11/2026 — Decisão: HOLD G2-a, NÃO editar ranges e NÃO iniciar VS_4BET.**

Novidade: equidade pré-flop física de 169 classes no HJ vs CO, ponderada pela política VS_OPEN do adversário, extraída de tabela externa previamente fornecida, validada quanto a cobertura e reciprocidade, e confrontada com Monte Carlo independente (15 classes × 50k simulações). O máximo desvio de validação aproximada foi 0,460 p.p.

AQo 41,31% (fold puro atual) supera o preço algébrico 31,43% de call com realização total e sem rake, mas fica aquém da exigência ilustrativa 44,11% sob EQR 75% e rake 5% (não observados). **A discrepância não prova fold errado**. AJo e A9o seguem muito abaixo desse exemplo de preço com EQR reduzida; pares baixos podem demandar estrutura pós-flop específica.

**Limitação crucial:** a tabela do usuário possui procedência/licença não documentada, por isso **não foi publicada em bruto**. Código/stdlb Monte Carlo e agregados 169 classes estão no GitHub, mas recriar o exato relatório original exige obter cópia autorizada com SHA documentado. Nenhuma política anterior mudou.

**Gate para mudança:** requer modelo confiável de realização de equidade e custo/rake específico, análise de ações remanescentes e EV de open+continuation por mão, regressões e documentação. Persistem G1 aberto, G2-a HOLD, G2-b bloqueado. Preservar DeepCrusher/CrusherTBP.
