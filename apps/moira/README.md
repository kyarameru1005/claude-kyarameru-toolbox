# moira

タスクと「再開コンテキスト」をプロジェクトルートの `.ai/moira.json` で管理する Rust 製 CLI。

長時間のオーケストレーションでメイン会話がトークン枯渇で要約されても、
`moira show` を読めば「目的・現在地・次の一手・決定ログ・タスク状態」から作業を再開できる。
ディスク上の `.ai/moira.json` を唯一の真実とし、会話の揮発に依存しない。

## ビルド

```bash
cd apps/moira
cargo build --release   # 実行ファイル: target/release/moira
cargo test
```

## 使い方

```bash
moira init                       # cwd に .ai/moira.json を作成
moira add "設計を書く"           # タスク追加（todo）
moira list                       # 一覧（[ ]=todo [~]=進行中 [x]=完了）
moira start 1                    # 進行中へ
moira done 1                     # 完了へ
moira status 2 in_progress       # 任意のステータスへ
moira remove 3                   # 削除

# 再開コンテキスト
moira goal "moira を完成させる"
moira at "実装中"
moira next "CI に Rust ジョブを足す"
moira decide "保存形式は JSON 単体に決定"

moira show                       # 再開ビュー（meta + タスク）
moira show --json                # 機械可読（エージェント連携用）
```

`init` 以外のコマンドは cwd から親方向へ `.ai/moira.json` を探索する。

## 保存形式（`.ai/moira.json`）

```json
{
  "version": 1,
  "next_id": 3,
  "meta": {
    "goal": "...",
    "current": "...",
    "next": "...",
    "decisions": [ { "at": "RFC3339", "text": "..." } ]
  },
  "tasks": [
    { "id": 1, "title": "...", "status": "todo", "created_at": "...", "updated_at": "..." }
  ]
}
```

- `status`: `todo` / `in_progress` / `done`
- `id` は単調増加で採番し、削除後も再利用しない（参照が安定）。
