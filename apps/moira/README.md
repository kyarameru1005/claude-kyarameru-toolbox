# moira

タスクと「再開コンテキスト」をプロジェクトルートの `.ai/moira.json` で管理する Rust 製 CLI。

長時間のオーケストレーションでメイン会話がトークン枯渇で要約されても、
`moira show` を読めば「目的・現在地・次の一手・決定ログ・タスク状態」から作業を再開できる。
ディスク上の `.ai/moira.json` を唯一の真実とし、会話の揮発に依存しない。

## インストール（Rust 不要）

ビルド済みバイナリを GitHub Releases から取得して PATH に入れる。Rust のインストールは不要。

> 安全性: インストーラは取得したバイナリの **sha256 をリリース同梱の `.sha256` と照合**し、
> 不一致や取得失敗時は中止する（fail-closed）。`curl | sh` を実行する前に、上のワンライナーの
> URL（取得元）が正しいかを必ず確認すること。検証付きの sha256 は `v*` タグのリリースから提供される。

### macOS / Linux

```bash
curl -fsSL https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.sh | sh
```

- OS / arch を自動判定して該当バイナリを取得し、既定では `~/.local/bin/moira` に配置する（**sudo 不要**）。
- `~/.local/bin` が PATH に無い場合はインストーラが警告するので、shell 設定に追加する。
- システム全体（`/usr/local/bin` など）へ入れたい場合のみ sudo を明示オプトイン:
  `curl -fsSL .../install.sh | BINDIR=/usr/local/bin MOIRA_SUDO=1 sh`
- 別の場所に入れたい場合: `curl -fsSL .../install.sh | BINDIR="$HOME/bin" sh`
- 特定バージョン: `curl -fsSL .../install.sh | MOIRA_VERSION=v0.1.0 sh`

### Windows（PowerShell）

```powershell
irm https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.ps1 | iex
```

- `%LOCALAPPDATA%\Programs\moira` に配置し、ユーザー環境変数 `Path` に追加する（新しいシェルで有効）。

インストール後は任意のリポジトリで `moira` が使える（`.ai/moira.json` を cwd から上方探索するため）。

対応プラットフォーム: macOS (Apple Silicon / Intel) ・ Linux x86_64 ・ Windows x86_64。

## アップデート

インストール用ワンライナーを再実行すると最新リリースへ更新される（既存バイナリを上書き）。

```bash
# macOS / Linux
curl -fsSL https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.sh | sh
```

```powershell
# Windows
irm https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.ps1 | iex
```

特定バージョンへ固定したい場合は `MOIRA_VERSION` を指定する。

## アンインストール

```bash
# macOS / Linux（既定 ~/.local/bin から削除。BINDIR を変えた場合は同じ値を渡す。
# 書き込み不可の場所は MOIRA_SUDO=1 を付ける）
curl -fsSL https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/uninstall.sh | sh
```

```powershell
# Windows（インストール先を削除し、ユーザー PATH からも除去）
irm https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/uninstall.ps1 | iex
```

各リポジトリの `.ai/moira.json`（タスク台帳）は削除されないため、不要なら手動で消す。

## ビルド（開発者向け）

ソースからビルドする場合（Rust 必要）:

```bash
cd apps/moira
cargo build --release   # 実行ファイル: target/release/moira
cargo test

# PATH に入れる
cargo install --path .   # ~/.cargo/bin/moira
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

## リリース手順（メンテナ向け）

バージョンタグを push すると、`.github/workflows/release.yml` が各プラットフォーム
（macOS arm64 / Intel・Linux x86_64・Windows x86_64）のバイナリをビルドし、
GitHub Releases にアップロードする。

```bash
# apps/moira/Cargo.toml の version を更新してから
git tag v0.1.0
git push origin v0.1.0
```

公開後、上記のインストール用ワンライナーが最新リリースを取得できるようになる。

