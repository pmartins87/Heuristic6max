#!/usr/bin/env python3
"""Verifica se o repositório realmente contém fontes de v0.5.
 Não declara testes aprovados: apenas detecta falta de arquivos."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "gto6_heuristic_v0_5"
ESSENTIAL = (
    "rfi_reference.py", "vs_open_reference.py", "vs_3bet_reference.py",
    "scenario_contract.py", "action_ledger.py", "strict_observation.py",
    "vs_3bet_bridge.py", "vs3_strategy_audit.py",
    "test_vs_3bet_reference.py", "test_vs3_strategy_audit.py",
    "RFI_100BB_169x5_DRAFT.csv", "VS_OPEN_100BB_15x169_DRAFT.csv",
    "VS_3BET_100BB_15x169_DRAFT.csv",
    "G2_VS3_Hand_Contributions_v0_5.csv",
    "G2_VS3_Composition_Summary_v0_5.csv",
    "SHA256SUMS.txt",
)

def main():
    missing = [name for name in ESSENTIAL if not (SRC/name).is_file()]
    if missing:
        print("CHECKPOINT INCOMPLETO: faltam fontes ou dados.")
        for f in missing:
            print("  MISSING:", f)
        print("Ação: importar o conteúdo extraído do pacote ZIP v0.5.")
        return 2
    print("Arquivos mínimos presentes. Executando testes (não equivale a validação GTO)...")
    r = subprocess.run([sys.executable, "-m", "unittest", "-q"], cwd=SRC)
    return r.returncode

if __name__ == "__main__":
    raise SystemExit(main())
