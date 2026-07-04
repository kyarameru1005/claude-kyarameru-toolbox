# トラブルシューティング

plugin marketplace の利用時によくある症状と確認手順です。

## スキル/プラグインが反映されない・発火しない

- `/reload-plugins` で再読み込みする。
- スキル名は `plugin名:スキル名` で名前空間化される（例: `/muse-tech:muse-tech`）。
  期待した名前で呼べない場合は、この名前空間込みの名前で呼んでいるか確認する。

## 更新が届かない（内容を変えたのに利用者に反映されない）

- 原因: plugin の `version` が据え置きだと同一版とみなされ、キャッシュされたまま更新が届かない。
- メンテナ側の対処: `.claude/skills/kairos-release/` の手順で version を上げて公開する。
- 利用者側の対処:
  ```text
  /plugin marketplace update kyarameru-claude
  /reload-plugins
  ```

## marketplace を改名した後に更新できない

- marketplace 名は現在 `kyarameru-claude`。旧名で登録済みの場合は一度削除してから再登録する。
  ```text
  /plugin marketplace remove <旧名>
  /plugin marketplace add kyarameru1005/claude-kyarameru-toolbox
  ```

## インストール済みの内容とリポジトリが食い違う

- `/plugin marketplace update kyarameru-claude` → `/reload-plugins` で同期する。

## プラグインキャッシュの場所

- `~/.claude/plugins/cache/` 配下にダウンロードされる。内容確認や掃除の目安として参照する。

## 依存が自動で入らない

- 依存は同一 marketplace 内の bare name 指定で、install 時に自動解決・自動導入される
  （詳細は [docs/plugins.md](plugins.md) を参照）。自動で入らない場合はまず上記の
  「更新が届かない」「インストール済みの内容とリポジトリが食い違う」を確認する。

## moira が使えない環境

`moira`（`apps/moira/`、タスク台帳 CLI）は zeus/olympus 運用でのタスク管理・再開コンテキスト保持に使う。

- `moira` コマンドが無い環境では、zeus/olympus 運用はインラインのチェックリスト
  （目的・現在地・完了済み・次の一手）で代替してよい。台帳の有無でタスクの長短による省略はしない。
- 導入したい場合は `apps/moira/README.md` のインストール手順を参照する
  （GitHub Releases のビルド済みバイナリを `apps/moira/install.sh` / `install.ps1` で導入、Rust 不要）。
- 台帳ファイル `.ai/moira.json` は `.gitignore` 済みで、リポジトリにはコミットしない。
