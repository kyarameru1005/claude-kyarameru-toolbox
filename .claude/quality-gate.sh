#!/usr/bin/env bash
# このリポジトリの品質ゲート（Tier 1: 速い・決定的なチェック）。
# dike-gate の発火点（git commit 直前 / 作業終了時）から実行される。
# 非0で終了するとコミット／終了がブロックされる。
set -euo pipefail

python3 scripts/validate.py
python3 -m pytest -q
