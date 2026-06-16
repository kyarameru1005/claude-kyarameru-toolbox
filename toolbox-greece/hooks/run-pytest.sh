#!/usr/bin/env bash
# PostToolUse フック: 編集対象が .py のときだけ pytest を走らせる。
# pytest が無い／テスト構成が無いプロジェクトでは何もしない（安全側で no-op）。
set -euo pipefail

input=$(cat)
file=$(printf '%s' "$input" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))' \
  2>/dev/null || true)

case "$file" in
  *.py) ;;
  *) exit 0 ;;
esac

command -v python3 >/dev/null 2>&1 || exit 0
python3 -c 'import pytest' >/dev/null 2>&1 || exit 0
[ -f pyproject.toml ] || [ -f pytest.ini ] || [ -f setup.cfg ] || [ -d tests ] || exit 0

python3 -m pytest -q
