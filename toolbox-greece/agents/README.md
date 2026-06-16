# agents

`toolbox-greece` のサブエージェント定義（frontmatter 付き `*.md`）を置く場所です。
役割名はギリシャ神話の神名で統一し、責務が名前から分かる状態を保ちます。

各エージェントは `skills/` の作業パターンと並行ペアになっています（`hermes` ↔ `labyrinth-explore` など）。
agent と skill のどちらを使うかの判断は、ルート `README.md` の「agents と skills の使い分け」を参照してください。

## エージェント一覧

| name | 役割 | 権限 | model |
|------|------|------|-------|
| `zeus` | Manager。判断と委譲、進行計画 | read-only | opus |
| `hermes` | 実装前調査。構造・依存・影響範囲 | read-only | sonnet |
| `daedalus` | 設計。責務分離・拡張性・選択肢比較 | read-only | opus |
| `hephaestus` | 実装。最小差分での変更 | write | sonnet |
| `athena` | 実装後レビュー。正しさ・保守性 | read-only | opus |
| `themis` | テスト・評価。合否判断 | read-only | sonnet |
| `ares` | セキュリティ・リスク検出 | read-only | opus |
| `apollo` | ドキュメント作成・更新 | write | sonnet |
| `chronos` | ログ・振り返り・再開メモ | read-only | haiku |

## 基本方針

- 1つのエージェントに複数の責務を詰め込まない。
- 調査、設計、実装、レビュー、検証、文書化、振り返りの責務を分ける。
- 書き込み権限を持つのは `hephaestus` と `apollo` のみに限定する。
- まず必要最小限の役割だけを使い、必要になったら増やす。

## オーケストレーション

- メインの Claude は全体判断と依頼の分配を担当する。
- 関連ファイルや影響範囲が不明なら、先に `hermes` を使う。
- 設計判断が必要なら、実装前に `daedalus` を使う。
- 実装後は `athena` や `themis` で確認する。
- 並列化は独立した作業だけに限定し、同じファイルを複数エージェントで同時に触らせない。
