# toolbox-greece

ギリシャ神話をモチーフにした Claude Code 設定の配布用 toolbox 第1号です。
役割ごとにサブエージェントを分け、必要なものだけを追加しながら育てる前提で使います。

## モチーフ

- 神々や英雄の名前を、調査、設計、実装、レビュー、検証などの役割名に対応させる。
- スキル名は神話の道具・場所・概念に対応させる。
- 名前は世界観の整理のために使い、設定はあくまで実務優先で設計する。

## 構成

- `CLAUDE.md`: 全体の行動原則
- `settings.json`: Claude Code の基本設定（権限の allow / deny を含む）
- `agents/`: 役割別サブエージェント定義（`zeus`, `hermes`, `daedalus`, `aphrodite`, `hephaestus`, `athena`, `themis`, `ares`, `khaos`, `apollo`, `chronos`）
- `skills/`: 作業パターン（`zeus-orchestrate`, `labyrinth-explore`, `oracle-design`, `muse-interface`, `muse-modern`, `muse-luxury`, `muse-minimal`, `muse-bold`, `muse-avantgarde`, `forge-implement`, `aegis-review`, `gauntlet-verify`, `pandora-chaos`, `chronicle-docs`, `argo-git-flow`, `atlas-repository`, `cerberus-permissions`）
- `commands/`, `hooks/`, `plugins/`, `mcp/`, `memory/`: 必要になった時点で使う拡張用ディレクトリ

## agents と skills の使い分け

`agents/` と `skills/` は同じ役割を別の使い方で提供する並行ペアです。

- **agents（神名）= 誰が担当するか。** 独立したコンテキストで調査や実装を任せ、メインの会話を汚さずに委譲したいときに使う。並列化や長い作業に向く。
- **skills（道具・概念）= どの型で進めるか。** メインの会話の中で、決まった手順・出力形式に沿って自分で進めたいときに使う。委譲のオーバーヘッドがない。

迷ったら「別コンテキストに任せたい → agent」「いまの会話で型に沿って進めたい → skill」で選びます。

| 役割 | agent | skill |
|------|-------|-------|
| オーケストレーション | `zeus` | `zeus-orchestrate` |
| 調査 | `hermes` | `labyrinth-explore` |
| 設計 | `daedalus` | `oracle-design` |
| UI/ビジュアル設計 | `aphrodite` | `muse-interface`（親）＋ 系統 `muse-*` |
| 実装 | `hephaestus` | `forge-implement` |
| レビュー | `athena` | `aegis-review` |
| 検証 | `themis` | `gauntlet-verify` |
| セキュリティ | `ares` | （`aegis-review` で兼ねる） |
| 耐障害性検証（カオス） | `khaos` | `pandora-chaos` |
| 文書化 | `apollo` | `chronicle-docs` |
| 振り返り・記録 | `chronos` | （`chronicle-docs` で兼ねる） |
| Git 作業 | （メイン Claude が担当） | `argo-git-flow` |
| 構造整理 | （メイン Claude が担当） | `atlas-repository` |
| 権限管理 | （メイン Claude が担当） | `cerberus-permissions` |

## 使い方

リポジトリルートで次を実行します。

```bash
# 1. 変更内容を確認（適用しない）
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --dry-run

# 2. 既存ファイルを壊さない範囲で適用
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --safe

# 3. 配布前に定義の妥当性を検証
python3 scripts/validate-toolbox.py toolbox-greece
```

詳しくはリポジトリルートの README を参照してください。

## オーケストレーション

- メインの Claude は全体判断と依頼の分配を担当する。
- 役割分担を明示したいときは `zeus` または `/zeus-orchestrate` から始める。
- 「調査 → 設計 → 実装 → レビュー → 検証 → 文書化」の順で必要な役割だけを選ぶ。
- 独立した作業（読み取り専用、または対象ファイルが重ならない）は並列グループとして同時に動かし、書き込みや順序依存は直列に保つ。
- 同じファイルを複数エージェントで同時に触らせない。独立性が判断できないときは直列にする。
