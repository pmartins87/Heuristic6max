#!/usr/bin/env python3
"""Verifica snapshots GitHub v0.5/v0.6 e executa a suíte atual.
Não avalia GTO, EV, rake, replay real ou jogabilidade.
"""
from __future__ import annotations
import csv
import hashlib
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
RELEASES={"v0.5":("gto6_heuristic_v0_5",51),
          "v0.6":("gto6_heuristic_v0_6",61)}

def check_manifest(folder:Path,expected_count:int):
    manifest=folder/"SHA256SUMS.txt"
    if not manifest.is_file():
        raise RuntimeError(f"Manifesto ausente: {manifest}")
    actual_files={p.name for p in folder.iterdir() if p.is_file()}
    with manifest.open(encoding="utf-8") as f:
        lines=[s.strip() for s in f if s.strip()]
    listed=set()
    for line in lines:
        sha,sep,name=line.partition("  ")
        if len(sha)!=64 or not sep or not name or "/" in name or "\\" in name:
            raise RuntimeError(f"Formato invalido de manifesto: {line[:80]}")
        p=folder/name
        if not p.is_file():
            raise RuntimeError(f"Arquivo faltante: {p}")
        got=hashlib.sha256(p.read_bytes()).hexdigest()
        if got != sha:
            raise RuntimeError(f"SHA256 diferente: {p.name}")
        listed.add(name)
    actual_files.discard("SHA256SUMS.txt")
    if listed!=actual_files:
        raise RuntimeError(f"Manifesto nao cobre todos os arquivos: {sorted(actual_files-listed)}, extras {sorted(listed-actual_files)}")
    if len(actual_files)+1!=expected_count:
        raise RuntimeError(f"Contagem diferente em {folder}: {len(actual_files)+1} != {expected_count}")

def check_preservation(folder:Path):
    path=folder/"V05_PRESERVATION_AUDIT_v0_6.csv"
    with path.open(encoding="utf-8",newline="") as f:
        rows=list(csv.DictReader(f))
    if len(rows)!=51 or any(x["Result"]!="SAME" or x["SHA256_v05"]!=x["SHA256_v06"] for x in rows):
        raise RuntimeError("Preservacao v0.5/v0.6 nao confirmada")
    for x in rows:
        earlier=(ROOT/"gto6_heuristic_v0_5"/x["File"])
        now=(ROOT/"gto6_heuristic_v0_6"/x["File"])
        if not earlier.exists() or not now.exists() or earlier.read_bytes()!=now.read_bytes():
            raise RuntimeError(f"Arquivo ancestral modificado: {x['File']}")

def main():
    try:
        for version,(subdir,count) in RELEASES.items():
            folder=ROOT/subdir
            check_manifest(folder,count)
            print(f"{version}: {count} arquivos e SHA256 verificados")
        check_preservation(ROOT/"gto6_heuristic_v0_6")
        print("v0.5 -> v0.6: 51/51 arquivos ancestrais identicos")
    except (RuntimeError,OSError,ValueError) as e:
        print(f"FALHA: {e}",file=sys.stderr)
        return 2
    src=ROOT/"gto6_heuristic_v0_6"
    result=subprocess.run([sys.executable,"-m","unittest","-q"],cwd=src)
    if result.returncode==0:
        print("Suíte v0.6 concluída. Validação estratégica e replays reais PENDENTES.")
    return result.returncode

if __name__=="__main__":
    raise SystemExit(main())
