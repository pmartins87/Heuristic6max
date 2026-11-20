# G3 — MVP prático de pós-flop SRP heads-up, flop/turn/river

**Checkpoint 20/11/2026. Módulo heurístico inspirado em GTO, não solver nem estratégia operacional validada.** Nenhum ajuste de ranges pré-flop. Este arquivo representa uma **primeira cobertura restrita das três streets**, com parâmetros conservadores e modificáveis. Não há dados de EV ou hipótese de qualidade GTO demonstrada; o projeto não precisa desses padrões acadêmicos para desenvolver heurísticas práticas, mas precisa evitar erros de execução.

## Entrega

- `srp_hu_postflop_draft.oppl`: **33 regras de ação OpenPPL**, 14 flop + 10 turn + 9 river, e cinco funções booleanas de domínio/força; única fonte das decisões.
- `preflop_and_srp_hu_draft.oppl`: **árvore única combinada** (RFI + VS_OPEN + VS_3BET inalterados e pós-flop), montada a partir da fonte GitHub `portability/vs_3bet_mvp/preflop_rfi_vsopen_vs3_draft.oppl`. Não são dois algoritmos divergentes.
- `srp_source_interpreter.py`: lê esse MESMO OpenPPL para testes offline, rejeita símbolos/sintaxe de fora da whitelist; não emite decisões para OpenHoldem.
- `test_srp_hu_mvp.py`: **18 testes novos** sobre ordem e prioridade de regras, valor, draws, price, c-bet dry 25%, turn barrel com NFD 30%, caller IP/OOP, isolamento HU e no-match, e identidade binária do pré-flop.
- `rebuild_combined.py`: utilitário *offline* de concatenação e checagem; não é código de runtime.
- `SRP_HU_SHA256SUMS.txt`: hashes para verificar integridade dos arquivos.

## Estratégia aproximada, em linguagem simples

- **Flop:** com overpair/top pair e kicker bom ou mãos feitas fortes, apostar por valor quando a ação chega sem aposta; com draw de flush nut, semivalue/semibluff seletivo. Em board seco sem pair e sem flush/straight possíveis, o agressor pré-flop faz c-bet pequeno a 25% de frequência via `randomhand`. Contra aposta, continuar com mãos e draws compatíveis com preço, desistir do restante.
- **Turn:** apostar por valor com mãos feitas fortes e boa top pair em linhas de iniciativa, barrel de nut-flush-draw a 30% de frequência; defender pelo preço. Outras mãos fazem check ou fold.
- **River:** apostar por valor com mãos fortes, apostar pequeno com boa top pair do agressor; calls conservadores orientados por tamanho, sem bluff river no MVP. O módulo não prevê ranges dinâmicos nem modelagem adversária.
- **Caller:** admite single-open/call pré-flop com um único adversário desde o flop. Aposta com mão forte e, em posição, pode apostar com top pair+kicker quando recebe check. 

## Condições e limites críticos

1. Considera apenas **6 jogadores que receberam cartas, um adversário desde o flop** (`OpponentsOnFlop = 1`, `OpponentsLeft = 1`), sem adversário all-in e sem estado de mesa desconhecido.
2. A árvore de abertura requer `BotRaisedBeforeFlop`, **sem call posterior do bot** e `NumberOfRaisesBeforeFlop = 0`. A árvore de defesa requer `BotCalledBeforeFlop`, sem raise do bot e `NumberOfRaisesBeforeFlop = 1`. A contagem é dos raises dos oponentes segundo o manual OpenPPL, portanto a distinção tem de ser confirmada na versão real do OpenHoldem.
3. **Limitação do histórico:** o manual não garante por esses símbolos isolados que não houve *limp/isolation raise*, squeezes com folds posteriores, ou mudanças da topologia do pote. Assim, a árvore é uma aproximação SRP-HU, não prova de identificação perfeita. Uma futura classificação com histórico mais confiável deve bloquear estados ambíguos, não inventar detalhes.
4. As apostas relativas `BetThirdPot`, `BetHalfPot`, `BetTwoThirdPot` e `RaiseHalfPot` estão documentadas no OpenPPL, mas têm legalidade/sizing final sujeita ao ambiente; ações calculadas podem ser adaptadas pelo OpenHoldem. **Não afirmar equivalência runtime.**
5. As funções `Have...` são símbolos OpenPPL e podem sobrepor várias categorias. A ordenação das regras é intencional; a prioridade `HaveNuts`/mão forte vem antes de draws e pares marginais.
6. **Sem `WHEN Others Fold/Check`:** para contexto fora do domínio, o simulador retorna `None`; o OpenHoldem pode executar um fallback. **Não carregar o arquivo em jogos com apostas** ou chamá-lo de bot pronto. O gate real G1/G6 requer replay sem apostas e inspeção de ação final.
7. Não cobre 3bet/4bet pots pós-flop, limped pots, multiway, shove, pot odds com rake real, decisões ótimas por texture e EQR. Esses continuam no roadmap.

## Reprodução de testes

Da raiz do repositório:

```sh
python -m unittest discover -s portability/srp_hu_mvp -p 'test_*.py' -q
python portability/srp_hu_mvp/rebuild_combined.py
git diff --exit-code -- portability/srp_hu_mvp/preflop_and_srp_hu_draft.oppl
(cd portability/srp_hu_mvp && sha256sum -c SRP_HU_SHA256SUMS.txt)
```

**Próximo passo com valor prático:** validar os símbolos de histórico/força de mão e a ação final em replay local desconectado do jogo real; depois adaptar as regras por textura em vez de só expandir um monte de condições. A revisão G2-a do pré-flop permanece aberta; os snapshots v0.6.1 são intocados.

**Fontes:** manual do projeto `OpenPPL Manual.pdf` (*BettingAction Symbols*, *Player and Opponent Symbols*, *Hand Symbols*, *Fixed Actions*, *Building Symbols On Your Own*, *History Symbols*), fornecido no pacote `OpenHoldem e OPPL Manuais e Library.zip`. Leitura não certifica que a instalação do usuário seja a mesma versão do manual.
