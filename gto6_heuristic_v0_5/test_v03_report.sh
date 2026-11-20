#!/usr/bin/env bash
set -euo pipefail
python -m unittest -v
python generate_v03_artifacts.py
python vs_open_reference.py
