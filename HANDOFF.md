# Guia de retomada — outros chats e outras IAs

**Leia antes de modificar qualquer coisa:** `README.md` → `PROJECT_STATE.md` → `ROADMAP.md` → `DECISIONS.md` → `CHANGELOG.md` → este guia. Examine commits e arquivos efetivamente presentes no GitHub, não confie só no texto de chats.

## Checkpoints
- v0.1: arquitetura, 22 testes.
- v0.2: RFI, 71 testes.
- v0.3: VS_OPEN, 91 testes.
- v0.4: VS_3BET, 114 testes.
- v0.5: composição por classe de mão, **119 testes**, *sem mudar decisões da v0.4*.

## Para executar o pacote completo v0.5
Após conferir presença e hashes dos arquivos:
```sh
cd gto6_heuristic_v0_5
python -m unittest -q
python vs3_strategy_audit.py
```
Dependência: Python 3.10+ e biblioteca padrão.

## Parada obrigatória
Se o ZIP v0.5, seus fontes e datasets **não estiverem no repositório**, o repositório é apenas um checkpoint documental incompleto. Não inventar os scripts ausentes; obter o ZIP original. Não afirmar que o código está versionado sem checar GitHub.

## Próximos passos
1. Conferir os arquivos efetivamente publicados.
2. Auditar por mão os oito `MAJOR_REVIEW`, usando relatórios de composição e observando que benchmarks têm rake/árvore diferentes.
3. Registrar novos testes e decisões; atualizar os seis documentos vivos.
4. Retomar VS_4BET **somente após** a revisão por classes e suas premissas.
5. G1 continua aberto até replays reais de teste e logs de ação final.

**Sem uso em mesas, sem autoplayer e sem alegar GTO verificada.**
## Verificação de identidade da entrega
Conferir [RELEASE_MANIFEST.md](RELEASE_MANIFEST.md) para o SHA-256 do ZIP v0.5 e o estado de replicação; só declarar a versão disponível quando os arquivos constarem no GitHub e passarem na verificação.
