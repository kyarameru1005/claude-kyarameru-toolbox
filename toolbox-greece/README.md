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
- `agents/`: 役割別サブエージェント定義（`zeus`, `hermes`, `daedalus`, `hephaestus`, `athena`, `themis`, `ares`, `apollo`, `chronos`）
- `skills/`: 作業パターン（`zeus-orchestrate`, `labyrinth-explore`, `oracle-design`, `forge-implement`, `aegis-review`, `gauntlet-verify`, `chronicle-docs`, `argo-git-flow`, `atlas-repository`）
- `commands/`, `hooks/`, `plugins/`, `mcp/`, `memory/`: 必要になった時点で使う拡張用ディレクトリ

## 使い方

リポジトリルートで次を実行します。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --dry-run
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --safe
```

詳しくはリポジトリルートの README を参照してください。

## オーケストレーション

- メインの Claude は全体判断と依頼の分配を担当する。
- 役割分担を明示したいときは `zeus` または `/zeus-orchestrate` から始める。
- 「調査 → 設計 → 実装 → レビュー → 検証 → 文書化」の順で必要な役割だけを選ぶ。
- 並列化は独立した作業だけに限定し、同じファイルを複数エージェントで同時に触らせない。
