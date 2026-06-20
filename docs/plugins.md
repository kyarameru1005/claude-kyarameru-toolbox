# Plugins 一覧と依存関係

このリポジトリが配布する plugin の構成です。各 plugin は `plugins/<category>/<name>/` に
自己完結し、共有はファイル複製ではなく `plugin.json` の `dependencies` で表します。

カテゴリ（ディレクトリ＝ marketplace の `category`）:

- `bundles/`: 依存だけの meta plugin（まとめパック）
- `roles/`: agent ＋ 作業スキル
- `workflow/`: 作業スキルのみ
- `design/`: muse-* デザイン系統

## まとめパック（依存だけの meta plugin）

中身（skill / agent）を持たず、依存する plugin をまとめて導入します。

| plugin | 依存（自動導入される plugin） |
| --- | --- |
| `greece-roles` | `zeus-orchestrate`, `labyrinth-explore`, `oracle-design`, `forge-implement`, `aegis-review`, `gauntlet-verify`, `chronicle-docs`, `pandora-chaos`, `atlas-repository`, `cerberus-permissions`, `argo-git-flow`, `agora-dialogue` |
| `muse-design` | `muse-interface`, `muse-modern`, `muse-minimal`, `muse-bold`, `muse-cute`, `muse-playful`, `muse-retro`, `muse-luxury`, `muse-editorial`, `muse-tech`, `muse-avantgarde`, `muse-immersive` |

## 役割系 plugin（agent ＋ 作業スキル）

| plugin | skill | agent |
| --- | --- | --- |
| `zeus-orchestrate` | zeus-orchestrate | zeus |
| `labyrinth-explore` | labyrinth-explore | hermes |
| `oracle-design` | oracle-design | daedalus |
| `forge-implement` | forge-implement | hephaestus |
| `aegis-review` | aegis-review | athena, ares |
| `gauntlet-verify` | gauntlet-verify | themis |
| `chronicle-docs` | chronicle-docs | apollo, chronos |
| `pandora-chaos` | pandora-chaos | khaos |

※ `ares`（セキュリティ）と `chronos`（記録・振り返り）は専用スキルを持たない例外のため、
概念的に近い `aegis-review` / `chronicle-docs` に同梱しています。

## 作業スキルのみ plugin（対応 agent なし）

`atlas-repository`, `cerberus-permissions`, `argo-git-flow`, `agora-dialogue`。

## デザイン系 plugin

`muse-interface` が基盤（親スキル ＋ `aphrodite` エージェント）。
各系統 plugin は skill のみを持ち、`dependencies: ["muse-interface"]` で基盤を取り込みます。

系統: `muse-modern`, `muse-minimal`, `muse-bold`, `muse-cute`, `muse-playful`,
`muse-retro`, `muse-luxury`, `muse-editorial`, `muse-tech`, `muse-avantgarde`, `muse-immersive`。

## 補足

- `zeus-orchestrate` 単体では、zeus が参照する他のサブエージェントは入りません。
  フル編成には `greece-roles` の導入を推奨します。
- 依存は同一 marketplace 内の bare name 指定で、install 時に自動解決・自動導入されます。
