# 権限ポリシー（PERMISSIONS.md）

`settings.json` はコメントを書けない厳密な JSON のため、各ルールの意味と理由をここに日本語で残す。
`settings.json` を変更したら、この表も同時に更新する（同期ずれに注意）。

- 対象リポジトリ: claude-kyarameru-toolbox
- 粒度プリセット: 標準
- 最終更新: 2026-06-20

## 層の責務

| 層 | ファイル | 役割 | コミット |
|----|----------|------|----------|
| user | `~/.claude/settings.json` | 全プロジェクト共通の安全策 | 対象外 |
| repo | `.claude/settings.json` | このリポジトリ固有の許可 | する |
| local | `.claude/settings.local.json` | 個人ローカル上書き | しない（.gitignore） |

優先順位は local > repo > user。`deny` はどの層でも最優先。

## allow（許可）

| ルール | 層 | 意味 / 理由 |
|--------|----|-------------|
| `Read` / `Grep` / `Glob` | repo | 読み取りは粗く許可 |
| `Bash(git status:*)` | repo | 状態確認は安全 |
| `Bash(git diff:*)` | repo | 差分確認は安全 |
| `Bash(git log:*)` | repo | 履歴参照は安全 |
| `Bash(git branch:*)` | repo | ブランチ確認・作成 |
| `Bash(git switch:*)` | repo | ブランチ切り替え |
| `Bash(git add:*)` | repo | ステージまでは許可 |
| `Bash(python3 -m pytest:*)` | repo | CLAUDE.md 指定のテストコマンド |
| `Bash(python3 scripts/validate.py:*)` | repo | marketplace / plugin 定義の検証コマンド |
| `Bash(moira:*)` | repo | タスク台帳 CLI（`.ai/moira.json`） |

## ask（都度確認）

| ルール | 層 | 意味 / 理由 |
|--------|----|-------------|
| `Bash(git commit:*)` | repo | 履歴を確定する操作 |
| `Bash(git push:*)` | repo | 外向き操作 |
| `Bash(gh pr:*)` | repo | 外向き操作（PR 作成） |

## deny（遮断）

| ルール | 層 | 意味 / 理由 |
|--------|----|-------------|
| `Bash(git push --force:*)` / `Bash(git push -f:*)` | repo（user にも） | 履歴破壊を遮断 |
| `Bash(git reset --hard:*)` | repo（user にも） | 作業消失を遮断 |
| `Bash(git clean:*)` | repo | 未追跡ファイル消失を遮断 |
| `Bash(rm -rf:*)` | repo（user にも） | 破壊操作を遮断 |
| `Read(./toolbox-*/.credentials.json)` | repo | 認証情報の読取を遮断 |
| `Read(./**/.env)` | repo | 秘密情報の読取を遮断 |

## メモ

- 未列挙の操作は ask に落ちる。運用しながら allow を足す。
- 破壊系の deny は user 層（`~/.claude/settings.json`）にもあり多重に遮断している。repo 層にも明示してリポジトリ単体で意図が読めるようにしている。
- cwd 外を許可したいときだけ `permissions.additionalDirectories` を使う（安易に広げない）。本リポジトリでは未使用。
- 秘密情報・トークン・マシン固有パスを設定値に書かない。
- 個人都合の緩和は `.claude/settings.local.json`（コミットしない）に置く。
