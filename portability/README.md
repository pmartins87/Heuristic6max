# Prova estática OpenPPL ↔ Python (PORT-0)

**NÃO EXECUTÁVEL COMO BOT; não carregar no OpenHoldem nem em mesas.**

- `portable_rfi_probe.oppl`: decisões autoradas **diretamente em OpenPPL** (duas condições BTN RFI, AA/KK). Não é perfil completo e não contempla stack efetivo/scraping.
- `oppl_probe.py`: executa as MESMAS linhas do arquivo `.oppl`, com parser whitelist extremamente restrito. Não é tradutor genérico nem máquina OpenHoldem.
- `test_oppl_probe.py`: 7 testes, dos quais um enumera 3.042 estados; rejeita syntax/comportamento fora da whitelist.

Execute da raiz do repositório:

```sh
python -m unittest discover -s portability -p 'test_*.py' -q
python portability/oppl_probe.py
```

**Não declarar paridade final:** falta verificação por motor OpenPPL real, incluindo resposta quando nenhuma regra corresponde, mapeamento de qualidade de observação, estabilidade de mix, estado de histórico, 6-max e legalidade. A semântica `None` do simulador de testes não garante que o OpenHoldem não faça uma ação por fallback.

## PORT-1 parcial (LJ RFI)

[port1/README.md](port1/README.md): 168 classes puras fielmente espelhadas em handlists/regras OpenPPL (43 RaiseTo, 125 Fold), 15 novos testes; KJo 40% RFI foi bloqueado. **Não carregar como bot:** falta evidência da paridade OpenHoldem-alvo.

## Gate G1/G6 offline — OH-G1G6-1
[Pacote de evidências](oh_runtime_gate_v1/README.md): 10 casos com campos de `f$debug`, `Best action` vs `Action taken`, pares de replay, identidade e SHA256, 26 testes. [CI OH-G1G6-1](https://github.com/pmartins87/Heuristic6max/actions/runs/44862638886) aprovou 599 execuções totais, 587 deduplicadas por suíte. O pacote **não é código executável para jogar** e mantém sempre `runtime_approved=false`. Última estratégia integrada permanece ISODEF-1; compatibilidade OpenHoldem real não demonstrada.

## OH-SRC1 — verificação estática baseada no código-fonte OpenHoldem
[Relatório OH-SRC1](oh_source_audit_v1/README.md): regressão de símbolos nativos OpenPPL, C++ com reset `user_*`, primeira órbita, `Set` e 436 comparações exatas de `PotSize`. [CI OH-SRC1](https://github.com/pmartins87/Heuristic6max/actions/runs/44864070437): 616 execuções em 31 suítes, 604 deduplicadas por suíte. **Não depende de fingerprint do software local para construir**, mas não substitui prova operacional do OpenHoldem. Fonte estratégica ISODEF-1 não foi editada.
