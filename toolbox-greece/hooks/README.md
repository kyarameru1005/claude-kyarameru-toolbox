# hooks

Claude Code のライフサイクルに反応する自動処理を置く場所です。
「変更のたびに必ず実行する」たぐいのルールは、プロンプトではなくここで自動化します。
（例: スクリプト変更後に `python3 -m pytest -q` を走らせる）

実体の設定は `settings.json` の `hooks` に書き、スクリプトをこのディレクトリに置きます。

この toolbox には `run-pytest.sh` を同梱済みで、`settings.json` から配線されています。
`Edit`/`Write` の後に、編集対象が `.py` で、かつ pytest とテスト構成があるプロジェクトのときだけ
`pytest -q` を実行します（条件を満たさなければ何もしない安全側の no-op）。

`apply` 後はユーザーの `~/.claude/hooks/run-pytest.sh` として配置され、`settings.json` の
`PostToolUse` から `"$HOME/.claude/hooks/run-pytest.sh"` で呼ばれます。
