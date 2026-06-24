#!/usr/bin/env bash
# 品質ゲート（Tier 1: 速い・決定的なチェック）。
#
# 使い方:
#   cp "$CLAUDE_PLUGIN_ROOT/templates/quality-gate.sh" .claude/quality-gate.sh
#   chmod +x .claude/quality-gate.sh
#   # 下の例を参考に、このプロジェクトのチェックを書く
#
# dike-gate plugin がコミット直前（git commit）と作業終了時（Stop）にこれを実行する。
# 非0で終了するとコミット／終了をブロックする。このファイルが無ければ素通り（no-op）。
set -euo pipefail

# 速い順に並べ、失敗したら即終了する。プロジェクトに合わせて編集する。
# 例:
#   ruff check .
#   ruff format --check .
#   python3 scripts/validate.py
#   python3 -m pytest -q

echo "quality-gate: チェック未設定です。.claude/quality-gate.sh を編集してください。" >&2
exit 0
