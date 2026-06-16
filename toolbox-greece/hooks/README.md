# hooks

Claude Code のライフサイクルに反応する自動処理を置く場所です。
「変更のたびに必ず実行する」たぐいのルールは、プロンプトではなくここで自動化します。
（例: スクリプト変更後に `python3 -m pytest -q` を走らせる）

実体の設定は `settings.json` の `hooks` に書き、スクリプトをこのディレクトリに置きます。
最小例（`settings.json` 側）:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [{ "type": "command", "command": "python3 -m pytest -q" }]
      }
    ]
  }
}
```
