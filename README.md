# claude-kyarameru-toolbox

Claude Code の役割別エージェントとデザイン系統スキルを、**plugin marketplace** として配布する
リポジトリです。必要な plugin だけを `/plugin install` で導入できます。

認証情報・履歴・ログ・セッションなどの実行時データは扱いません。配布するのは再利用できる
スキルとエージェントの定義だけです。

## 使い方

marketplace を追加し、欲しい plugin を入れます。

```text
/plugin marketplace add kyarameru1005/claude-kyarameru-toolbox
/plugin install greece-roles@kyarameru-claude     # 役割別エージェント＋作業スキル一式
/plugin install muse-design@kyarameru-claude       # デザイン系統スキル一式
/plugin install muse-tech@kyarameru-claude         # 個別スキルだけ（依存 muse-interface も自動導入）
```

CLI でも同じことができます。

```bash
claude plugin marketplace add kyarameru1005/claude-kyarameru-toolbox
claude plugin install muse-tech@kyarameru-claude
```

導入後はスキルが `plugin名:スキル名` で名前空間化されます（例: `/muse-tech:muse-tech`）。
反映には `/reload-plugins` を使います。

## 配布する plugin

### まとめパック（依存だけを束ねた meta plugin）

- `greece-roles`: Zeus と役割別サブエージェント、調査・設計・実装・レビュー・検証・文書化の作業スキル一式。
- `muse-design`: `muse-*` デザイン系統スキル一式（基盤 `muse-interface` を含む）。

### 個別 plugin

- 役割系: `olympus-orchestrate`, `labyrinth-explore`, `oracle-design`, `forge-implement`,
  `aegis-review`, `gauntlet-verify`, `chronicle-docs`, `pandora-chaos`, `panacea-debug`,
  `atlas-repository`, `cerberus-permissions`, `argo-git-flow`, `agora-dialogue`,
  `dike-gate`, `mnemosyne-memory`, `hestia-bootstrap`。
- デザイン系: `muse-interface`（基盤）, `muse-modern`, `muse-minimal`, `muse-bold`,
  `muse-cute`, `muse-playful`, `muse-retro`, `muse-luxury`, `muse-editorial`,
  `muse-tech`, `muse-avantgarde`, `muse-immersive`。

各 plugin の中身と依存関係は [docs/plugins.md](docs/plugins.md) を参照してください。

## リポジトリ構造

- `.claude-plugin/marketplace.json`: 配布カタログ（全 plugin を列挙、`category` 付き）。
- `plugins/<category>/<name>/`: 1 インストール単位。`.claude-plugin/plugin.json` ＋ `skills/` `agents/`。
  カテゴリは `bundles/`（まとめパック）, `roles/`（agent＋skill）, `workflow/`（skill のみ）, `design/`（muse-*）。
- `apps/moira/`: タスク台帳 CLI（Rust）。GitHub Releases で配布。
- `scripts/validate.py`: marketplace と各 plugin の検証スクリプト。
- `tests/`: 検証スクリプトの単体テスト。
- `docs/`: plugin 一覧と貢献手順。

## 開発と検証

```bash
python3 -m pip install -e '.[dev]'   # 初回のみ
python3 scripts/validate.py          # marketplace と全 plugin を検証
python3 -m pytest -q                 # テスト
claude plugin validate .             # ネイティブ検証（任意）
```

新しい plugin の追加手順は [docs/contributing.md](docs/contributing.md) を参照してください。
反映されない・更新が届かないなどの問題は [docs/troubleshooting.md](docs/troubleshooting.md) を参照してください。
バージョンごとの変更点は [CHANGELOG.md](CHANGELOG.md) を参照してください。

## ライセンス

[MIT License](LICENSE) © 2026 kyarameru1005
