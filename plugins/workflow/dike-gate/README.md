# dike-gate

コミット直前（`git commit`）と作業終了時（`Stop`）に品質チェックを強制する品質ゲート。
各リポジトリの `.claude/quality-gate.sh` を hooks で実行し、失敗すればコミットや終了をブロックする。
スクリプトが無ければ素通り（no-op）。

## 構成

- `hooks/hooks.json` … `PreToolUse(git commit)` と `Stop` で `hooks/run-gate.sh` を実行。
- `hooks/run-gate.sh` … プロジェクトの `.claude/quality-gate.sh` を実行し、失敗時に commit を deny / stop を block する。
- `templates/quality-gate.sh` … 各リポジトリの `.claude/quality-gate.sh` に置く雛形。
- `skills/dike-gate` … セットアップと運用方針を示すスキル。

## セットアップ

```sh
cp "$CLAUDE_PLUGIN_ROOT/templates/quality-gate.sh" .claude/quality-gate.sh
chmod +x .claude/quality-gate.sh
# .claude/quality-gate.sh にこのプロジェクトのチェック（lint・テスト・検証）を書く
```

ローカルの速い関門（hooks）と、確実な関門（CI）の併用を推奨します。
