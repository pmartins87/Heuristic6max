# ADR-015 — Fonte estratégica, compatibilidade e limite de auditoria

**Decisão:** preservar todas as decisões de pôquer v0.6.1 e os resultados v0.7–v0.10; criar um catálogo verificável de fontes públicas e um gate fail-closed de admissibilidade. Não importar frequências no motor, não editar RFI/VS_OPEN/VS_3BET e não iniciar VS_4BET ou conversão OpenPPL.

**Evidência nova:** para o nó HJ abre 2,5 BB, CO 3-bet a 8 BB, nenhuma das três referências públicas examinadas teve **todos** os campos verificados. ART/GTO HJ RFI usa 2 BB e é um nó diferente; a árvore comercial publicada pelo Simple GTO informa 2,5 BB e 3,4× em posição (8,5 BB inferido, não validado para o nó específico); GTO Wizard exige selecionar/verificar a solução. Rake/cap da plataforma-alvo e permissões para incorporação não estão documentados.

**Justificativa econômica e de compute:** continuar fazendo auditorias de call/fold sob EQR/rake arbitrários dificilmente mudará a decisão. A próxima ação tecnicamente útil é obter premissas econômicas e fontes compatíveis ou validar o pipeline G1 com replays de teste. O gate de fontes **não substitui** a engenharia heurística necessária para situações sem cobertura.

**G6:** Python = implementação atual; OpenPPL/OpenHoldem = interface planejada, sem fonte executável. Preservar contrato `None` para estados ausentes ou inválidos.

**Estado:** G0 aprovado, G1 aberto, G2-a HOLD, G2-b bloqueado, G3–G7 pendentes. Nada operacional.
