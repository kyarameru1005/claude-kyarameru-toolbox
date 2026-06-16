# 権限ポリシー（PERMISSIONS.md）

`settings.json` はコメントを書けない厳密な JSON のため、各ルールの意味と理由をここに日本語で残す。
`settings.json` を変更したら、この表も同時に更新する（同期ずれに注意）。

- 対象リポジトリ: <リポジトリ名>
- 粒度プリセット: 粗め / 標準 / 厳格 のいずれか（<選んだもの>）
- 最終更新: YYYY-MM-DD

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
| `Bash(git status:*)` 他 git 参照 | repo | 状態確認は安全 |
| `Bash(git add:*)` | repo | ステージまでは許可 |
| `Bash(python3 -m pytest:*)` | repo | このリポジトリの検証コマンド |
| `Edit(<dir>/**)` | repo | 編集を対象ディレクトリに限定（cwd 外編集を防ぐ） |

## ask（都度確認）

| ルール | 層 | 意味 / 理由 |
|--------|----|-------------|
| `Bash(git commit:*)` | repo | 履歴を確定する操作 |
| `Bash(git push:*)` | repo | 外向き操作 |
| `Bash(gh pr:*)` | repo | 外向き操作 |
| `WebFetch` | repo | 外部取得は確認 |

## deny（遮断）

| ルール | 層 | 意味 / 理由 |
|--------|----|-------------|
| `Bash(git push --force:*)` / `-f` | user | 履歴破壊を遮断 |
| `Bash(git reset --hard:*)` | user | 作業消失を遮断 |
| `Bash(git clean:*)` | repo | 未追跡ファイル消失を遮断 |
| `Bash(rm -rf:*)` | user | 破壊操作を遮断 |
| `Read(./**/.env)` / `Read(./**/.env.*)` | repo | 秘密情報の読取を遮断 |
| `Read(./**/.credentials.json)` | repo | 認証情報の読取を遮断 |
| `Read(./**/secrets/**)` | repo | 機密ディレクトリの読取を遮断 |

## メモ

- 未列挙の操作は ask（または `permissions.defaultMode`）に落ちる。運用しながら allow を足す。
- cwd 外を許可したいときだけ `permissions.additionalDirectories` を使う（安易に広げない）。
- 秘密情報・トークン・マシン固有パスを設定値に書かない。
