# CLAUDE.md

このリポジトリ自体で作業するときの行動原則です。

- 日本語で簡潔に応答する。
- 推測より確認を優先する。
- 変更は必要最小限にとどめる。
- 破壊的操作やリポジトリ外の変更は事前に確認する。
- 秘密情報や実行時データは追加しない。
- スクリプトを変更したら `python3 -m pytest -q` を実行する。
- plugin / marketplace の定義（`plugins/`, `.claude-plugin/marketplace.json`）を変更したら `python3 scripts/validate.py` を実行する。

## 配布構造（plugin marketplace）

- このリポジトリは Claude Code の plugin marketplace。`/plugin marketplace add` → `/plugin install` で配布する。
- `plugins/<category>/<name>/` が 1 インストール単位（自己完結）。`.claude-plugin/plugin.json` ＋ `skills/` `agents/` で構成する。カテゴリは `bundles`/`roles`/`workflow`/`design`。
- 共有はファイル複製ではなく plugin 依存（`plugin.json` の `dependencies`）で表す。まとめパックは中身を持たない依存専用 plugin にする。
- 全 plugin を `.claude-plugin/marketplace.json` に列挙する（`source` は `./plugins/<category>/<name>`、`category` 付き）。

## スキル / エージェントの使用範囲

- `plugins/` 配下のスキルやエージェント定義は、このリポジトリでは編集・検証の対象としてのみ扱い、直接の利用対象にしない。
- 実行時に利用してよいのは、次に登録されたスキル / エージェントのみとする。
  - リポジトリルートの `.claude/`（`.claude/skills`, `.claude/agents`）
  - ユーザーグローバルの `~/.claude/`（`~/.claude/skills`, `~/.claude/agents`）

## 配布時のセキュリティ

このリポジトリは他環境へ配布される前提のため、コミット前に次を守る。

- 絶対パスやマシン固有パス（`/Users/...`, `/home/...`, ユーザー名）を追跡ファイルに書かない。ホーム参照は `~` か `$HOME` を使う。
- 秘密情報（API キー・トークン・認証情報・秘密鍵・`.env`）をコミットしない。値は環境変数や secret 参照で渡し、設定ファイルに直書きしない。
- 実行時データ・個人状態（`.ai/`、ログ、セッション、`settings.local.json` など）はコミットしない（`.gitignore` を維持する）。
- 配布する `settings.json` は最小権限にする。破壊操作（`rm -rf`、force push、`reset --hard`）は `deny`、外向き通信・書き込み系は `ask` 寄りにする。
- hooks やスクリプトは安全側で書く（`set -euo pipefail`、対象が無ければ no-op、入力を検証）。絶対パスを書かず `$HOME` 相対にする。
- 外部からコードを取得して実行する導線（`curl | sh` など）は、取得元を固定し、可能なら配布物のチェックサム／署名を検証する。
- MCP や外部接続は、接続先・必要な権限・取得する情報の範囲を最小限にする。秘密は環境変数で渡す。
- 配布前に、追跡ファイルへ絶対パスや秘密情報が混入していないか grep で確認する。
