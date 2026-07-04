#!/usr/bin/env bash
# このリポジトリの品質ゲート（Tier 1: 速い・決定的なチェック）。
# dike-gate の発火点（git commit 直前 / 作業終了時）から実行される。
# 非0で終了するとコミット／終了がブロックされる。
set -euo pipefail

# ローカルに ruff があれば lint / format を確認する（CI でも必ず検証する）。
if command -v ruff >/dev/null 2>&1; then
  ruff check .
  ruff format --check .
else
  echo "ruff 未導入のためローカル lint をスキップ（CI で検証）。pip install -e '.[dev]' を推奨" >&2
fi
python3 scripts/validate.py
python3 -m pytest -q
