# Como continuar o Heuristic6max em outro chat ou por outra IA

1. Abrir `https://github.com/pmartins87/Heuristic6max` e ler **nesta ordem**: `README.md`, `PROJECT_STATE.md`, `ROADMAP.md`, `DECISIONS.md`, `CHANGELOG.md` e este `HANDOFF.md`.
2. Conferir o hash do commit principal e os hashes do pacote fonte usado. Nunca presumir que um link antigo de conversa contém a versão atual.
3. Buscar código-fonte e datasets versionados no repositório. Se houver apenas documentação, o código não está replicado: recuperar o pacote ZIP v0.5 antes de modificar qualquer algoritmo. **Não inventar código ausente.**
4. Reproduzir suíte (`python -m unittest -q`) com Python >= 3.10 na pasta do pacote. v0.5 tem 119 testes unitários aprovados nesta sessão, ainda sem replays reais.
5. Escopo de política VS_3BET: 6 jogadores, stacks 95-105 BB, RFI fixo 2.5 BB (3 BB SB), 3-bet de sizing definido, sem limpers/callers/squeeze/short stack. Os 15 pares e 169 classes são **DRAFT**.
6. O avanço imediatamente recomendado é revisar classes e composição dos oito nós `MAJOR_REVIEW` de VS_3BET, priorizando `SB-BB`, `HJ-CO`, `LJ-CO`, `CO-BTN` e `HJ-BTN`; não forçar convergência de agregados entre árvores distintas.
7. Reportar evidência, novos testes, alterações e suas razões. Atualizar documentos vivos e checkpoints em cada entrega. Não alterar DeepCrusher, CrusherTBP ou AoF.
8. Não operar com dinheiro real nem chamar políticas DRAFT de GTO. Ausência de política (None) deve permanecer explícita.

## Checkpoints
- v0.1 arquitetura/contratos: 22 testes.
- v0.2 RFI: 71 testes.
- v0.3 VS_OPEN: 91 testes.
- v0.4 VS_3BET: 114 testes.
- v0.5 auditoria detalhada e documentação GitHub: 119 testes. **Não altera as decisões da v0.4.**

## Comandos locais
```sh
cd gto6_heuristic_v0_5
python -m unittest -q
python vs3_strategy_audit.py
python generate_v04_artifacts.py
```

`G1_Replay_Real_Protocolo.md` permanece a especificação para coletar evidência de replays reais, ainda não executada.
