# plugins

配布する plugin を置くディレクトリです。各 plugin は `plugins/<category>/<name>/` に
自己完結し、`.claude-plugin/marketplace.json` から `source: "./plugins/<category>/<name>"`
で参照されます。

## カテゴリ

- `bundles/`: 依存だけを束ねた meta plugin（まとめパック）。中身は持たない。
  - `greece-roles`, `muse-design`
- `roles/`: サブエージェント ＋ 対応する作業スキル。
  - `zeus-orchestrate`, `labyrinth-explore`, `oracle-design`, `forge-implement`,
    `aegis-review`, `gauntlet-verify`, `chronicle-docs`, `pandora-chaos`
- `workflow/`: 作業スキルのみ（対応する agent なし）。
  - `atlas-repository`, `cerberus-permissions`, `argo-git-flow`, `agora-dialogue`, `mnemosyne-memory`
- `design/`: muse-* デザイン系統。基盤 `muse-interface` ＋各系統。
  - `muse-interface`, `muse-modern`, `muse-minimal`, `muse-bold`, `muse-cute`,
    `muse-playful`, `muse-retro`, `muse-luxury`, `muse-editorial`, `muse-tech`,
    `muse-avantgarde`, `muse-immersive`

## 1 plugin の構成

```
plugins/<category>/<name>/
├── .claude-plugin/plugin.json   # name / version / description / dependencies
├── skills/<skill>/SKILL.md      # 作業スキル（任意）
├── agents/<agent>.md            # サブエージェント（任意）
└── README.md
```

- 共有はファイル複製ではなく `plugin.json` の `dependencies` で表す。
- 一覧と依存関係は [../docs/plugins.md](../docs/plugins.md)、追加手順は
  [../docs/contributing.md](../docs/contributing.md) を参照。
- 追加・変更したら `python3 scripts/validate.py` で検証する。
