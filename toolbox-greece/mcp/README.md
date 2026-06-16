# mcp

MCP（Model Context Protocol）サーバー設定を置く場所です。
外部ツールやデータソースへ接続する必要が出たときに使います。

秘密情報（API キー・トークン）は設定ファイルに直接書かず、環境変数で渡します。
追加するときは、接続先・必要な権限・取得する情報の範囲を最小限に保ちます。

## 同梱の推奨サーバー（`servers.json`）

開発で役立つ、API キー不要で導入しやすいものを入れています。

| name | 役割 | 相性 |
|------|------|------|
| `context7` | ライブラリ/フレームワークの最新ドキュメントを取得（読み取り中心） | `labyrinth-explore` / `forge-implement` |
| `playwright` | 実ブラウザ操作・E2E・スクリーンショット | `verify` / `run` |

前提: Node.js 18+。`playwright` は初回起動時にブラウザを自動ダウンロードします。

## 有効化方法

Claude Code は通常プロジェクトルートの `.mcp.json` を読みます。次のどちらかで有効化します。

- 方法A: `servers.json` の `mcpServers` を、プロジェクトルートの `.mcp.json` にマージする。
- 方法B: CLI で追加する。
  ```bash
  claude mcp add context7 npx -y @upstash/context7-mcp
  claude mcp add playwright npx -y @playwright/mcp@latest
  ```

## 秘密情報・権限

- `context7`: ローカル `npx` 利用では API キー不要。リモート利用やレート上限緩和に使う場合のみ、
  `CONTEXT7_API_KEY` を環境変数で渡す（設定ファイルに直書きしない）。
- `playwright`: API キー不要。ローカルでブラウザを起動する。
- `cerberus-permissions` と整合させ、MCP ツールの allow / ask を明示する。外向き通信や書き込み系は ask 寄りにする。
