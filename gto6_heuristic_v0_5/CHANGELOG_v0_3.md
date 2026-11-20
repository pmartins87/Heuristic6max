# GTO Heuristic 6-Max — Changelog v0.3

20/11/2026 — base de v0.2 preservada e avanço controlado do G2 VS_OPEN.

## Adicionado
- `vs_open_reference.py`: 15 confrontos opener×hero com 169 classes de mão cada; 2.535 políticas DRAFT; grupos explícitos de 3-bet/call/fold com frequências mistas por grupo e dimensionamento 3bet-to conforme IP/OOP.
- `vs_open_bridge.py`: gate contra historico incompleto, limpers, callers, squeeze, open diferente 2,5/3 BB e stacks fora 95-105 BB; só entra a partir de snapshots consistentes.
- `evidence_ingest.py`: leitor de fixtures canônicas de ações confirmadas manualmente. Não é parser de OpenHoldem.
- 20 novos testes comparados à v0.2, total 91, incluídos 2.535 cenários sintéticos da bridge.
- CSV completo VS_OPEN, benchmark crosscheck, sombras de hand ranges e inventário de nós.

## Corrigido durante a iteração
- O `SHOVE` que não reabre a ação causava erro após possível mutação. Agora valida preempitivamente: erro é atômico.
- `expected_pot_bb('SB')`: open de 3 BB do SB soma 3+1 BB, não 3+1,5 BB, pois SB já tinha investido 0,5 BB.
- Grupo `mix3c` do SB gera 3-bet/fold, nunca call OOP, em conformidade com a decisão de modelagem rake-unknown atual.
- Massa de defesa do BB foi revisada uma vez a partir de ranges explícitos por mão, com benchmarks externos apenas como controle: não há promessa de GTO exato.

## Auditorias abertas
- Três diferenças de frequência de 3-bet superiores a 3pp contra ART/GTO em CO vs LJ, CO vs HJ, BTN vs HJ. Rake/opções de aposta diferentes; não corrigir só por aproximação de número agregado.
- 174 registros de mãos em grupos de call também cobertos por grupo agressivo; precedência documentada, revisão editorial futura recomendada.
- Todos os conjuntos de 169 mãos exigem revisão estratégica, especialmente mãos marginais e posições iniciais.
- Nenhum log de mesa **6-max real** foi anexado ou verificado nesta execução; G1 permanece aberto.
- Condições de rake/site não conhecidas; G2 não pode ser certificado.
- Falta VS_3BET, VS_4BET, cold 4-bet, squeeze, limp, 5-bet, shove e outros stacks.

## Decisões mantidas
- Projeto heurístico, **sem solver obrigatório**.
- Versões e algoritmos do DeepCrusher/CrusherTBP permanecem inalterados.
- Nenhum OpenPPL operacional/ação live enquanto G1/G2 não passarem pelos gates.
- Fonte de verdade é README v0.3 + Changelog v0.3 + arquivos de código/teste.
