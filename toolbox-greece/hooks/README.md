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

`run-validate-toolbox.sh` も同梱・配線済みです。`Edit`/`Write` の後に、編集対象が
`agents/*.md` または `skills/*/SKILL.md` で、かつ `scripts/validate-toolbox.py` があるときだけ
その toolbox に対して `validate-toolbox.py` を実行します（条件を満たさなければ no-op）。
agent / skill 定義の整合（必須キー・name 一致・README 一覧）を変更直後に自動検証する目的です。
