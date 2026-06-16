#!/usr/bin/env bash
# PostToolUse フック: agent / skill 定義（agents/*.md, skills/*/SKILL.md）を
# 編集したときだけ validate-toolbox.py を走らせる。
# 検証スクリプトが無い配布先などでは何もしない（安全側で no-op）。
set -euo pipefail

input=$(cat)

# 編集対象ファイルから、所属する toolbox 名（agents/skills の親ディレクトリ名）を取り出す。
# agents/README.md など対象外は空文字を返す。
toolbox=$(printf '%s' "$input" | python3 -c '
import json, re, sys
try:
    file = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
except Exception:
    sys.exit(0)
m = re.search(r"/([^/]+)/agents/[^/]+\.md$", file)
if m and not file.endswith("/README.md"):
    print(m.group(1)); sys.exit(0)
m = re.search(r"/([^/]+)/skills/[^/]+/SKILL\.md$", file)
if m:
    print(m.group(1))
' 2>/dev/null || true)

[ -n "$toolbox" ] || exit 0

command -v python3 >/dev/null 2>&1 || exit 0
[ -f scripts/validate-toolbox.py ] || exit 0

python3 scripts/validate-toolbox.py "$toolbox"
