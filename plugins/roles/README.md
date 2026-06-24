# roles

役割別のサブエージェントと、それに対応する作業スキルをまとめた plugin カテゴリです。
各 plugin は `plugins/roles/<name>/` に自己完結し、`skills/` ＋ `agents/` で構成します。

`olympus-orchestrate`（Zeus）を入口に、調査 → 設計 → 実装 → レビュー → 検証 → 文書化の
流れを役割ごとに切り出して使います。

## plugin 一覧

| plugin | 役割 | サブエージェント |
| --- | --- | --- |
| `olympus-orchestrate` | オーケストレーション（役割分担と進行計画） | zeus |
| `labyrinth-explore` | 実装前のコード構造・影響範囲の調査 | hermes |
| `oracle-design` | 構造・責務・アーキテクチャ方針の設計 | daedalus |
| `forge-implement` | 最小差分での実装・修正 | hephaestus |
| `aegis-review` | レビュー（保守性 athena ／リスク・セキュリティ ares） | athena, ares |
| `gauntlet-verify` | テスト・検証と合否判断 | themis |
| `chronicle-docs` | ドキュメント（apollo）と実行ログ・振り返り（chronos） | apollo, chronos |
| `pandora-chaos` | カオス実験の設計＋コンテナ隔離での安全な注入 | khaos |

8 plugin をまとめて導入するには bundles の `greece-roles` を使います。

## 1 plugin の構成

```
plugins/roles/<name>/
├── .claude-plugin/plugin.json   # name / version / description
├── skills/<name>/SKILL.md       # 作業スキル
├── agents/<agent>.md            # サブエージェント（1つ以上）
└── README.md
```

## 使い方

- 入口は `olympus-orchestrate`。Zeus が何を自分で処理し、どの役割へ委譲するかを判断する。
- 各 plugin はスキルで作業手順を、サブエージェントで委譲先を提供する。
- 詳細は各 plugin の `README.md`、一覧と依存は [../../docs/plugins.md](../../docs/plugins.md) を参照。
- 追加・変更したら `python3 scripts/validate.py` で検証する。
