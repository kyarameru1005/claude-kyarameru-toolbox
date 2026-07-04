#!/usr/bin/env bash
# dike-gate: フックから呼ばれ、プロジェクトの品質ゲートを実行する。
# - PreToolUse(git commit) と Stop の両方から呼ばれる。
# - 対象は "$CLAUDE_PROJECT_DIR/.claude/quality-gate.sh"。無ければ素通り（no-op）。
# - ゲートが失敗したら、イベント別に JSON 判定を出して commit / stop をブロックする。
set -euo pipefail

# フック JSON を読む（stdin）
input="$(cat)"

project_dir="${CLAUDE_PROJECT_DIR:-$PWD}"
gate="$project_dir/.claude/quality-gate.sh"

# ゲート未設置・非実行なら素通り
if [ ! -x "$gate" ]; then
  exit 0
fi

# フックイベント名を取得（失敗しても続行）
event="$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("hook_event_name",""))' 2>/dev/null || true)"

# ゲート実行（出力を捕捉）。成功なら許可／停止可。
if output="$(cd "$project_dir" && bash "$gate" 2>&1)"; then
  exit 0
fi

# 失敗 → イベント別に JSON 判定を出力（exit 0 で構造化制御）
export GATE_OUTPUT="$output"
export GATE_EVENT="$event"
python3 <<'PY'
import json, os

out = os.environ.get("GATE_OUTPUT", "")
event = os.environ.get("GATE_EVENT", "")
tail = out[-3000:] if len(out) > 3000 else out
summary = "品質ゲート（.claude/quality-gate.sh）が失敗しました。修正してから再試行してください。"

if event == "PreToolUse":
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": summary,
            "additionalContext": tail,
        }
    }, ensure_ascii=False))
elif event == "Stop":
    print(json.dumps({
        "decision": "block",
        "reason": summary,
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": tail,
        }
    }, ensure_ascii=False))
else:
    # 不明イベントは情報提示にとどめる
    print(json.dumps({"systemMessage": summary}, ensure_ascii=False))
PY
exit 0
