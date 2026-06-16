# claude-kyarameru-toolbox

Claude Code の設定一式を toolbox として管理し、必要な toolbox だけを `~/.claude` へ安全に適用するためのリポジトリです。

[kyarameru-tool-box](https://github.com/kyarameru1005/kyarameru-tool-box)（Codex 版）を参考に、Claude Code 向けへ作り直したものです。

認証情報、履歴、ログ、セッション、DB、キャッシュなどの実行時データは扱いません。
このリポジトリで配布するのは、再利用できる設定ファイルと設定ディレクトリだけです。

## Toolbox

- `toolbox/`: 初期状態へ戻すための最小 toolbox。
- `toolbox-greece/`: 設定済み toolbox 第1号。Zeus などの役割別サブエージェントと作業スキルを含みます。
- `toolbox-名前/`: 今後追加する配布用 toolbox。用途やテーマごとに増やします。

## まず使う

1. 現在の状態を確認します。

```bash
python3 scripts/toolbox-manager.py status
```

2. `toolbox-greece/` を適用した場合の変更内容を確認します。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --dry-run
```

3. 問題なければ、バックアップ付きで `~/.claude` へ適用します。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --safe
```

4. 初期状態へ戻したい場合も、先に dry-run します。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox --dry-run
python3 scripts/toolbox-manager.py apply --toolbox toolbox --safe
```

詳しい導入手順は [Getting Started](docs/distribution/getting-started.md) を参照してください。

## できること

- toolbox を `~/.claude` へ安全に適用する。
- 適用前に `--dry-run` で変更予定を確認する。
- `--safe` で既存設定をバックアップしてから置換する。
- `toolbox/` から新しい `toolbox-名前/` を作る。
- 適用済みの管理対象を `~/.claude/.claude-kyarameru-toolbox-manifest.json` に記録する。

## コマンド

### status

```bash
python3 scripts/toolbox-manager.py status [--toolbox toolbox] [--claude-home ~/.claude]
```

指定した toolbox と `~/.claude` の管理対象を比較し、`current`, `different`, `missing` を表示します。

### apply

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --dry-run
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --safe
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --force
```

指定した toolbox を `~/.claude` へ置換します。

- `--dry-run`: 変更予定だけを表示する。
- `--safe`: バックアップ付きで置換する。
- `--force`: バックアップなしで置換する。

通常は `--dry-run` のあとに `--safe` を使ってください。
`--force` はバックアップ不要と判断できる場合だけ使います。

### copy

```bash
python3 scripts/toolbox-manager.py copy [--source toolbox] [--name greece] [--dry-run]
```

`--source` で指定した toolbox を、`--name` で指定した `toolbox-名前/` へ複製します。
認証情報、履歴、DB、ログ、セッション、キャッシュなどの除外対象は複製しません。

## 置換対象

`apply` が `~/.claude` で置き換える対象は次に限定します。
空ディレクトリ保持用の `.gitkeep` は置換対象に含めません。

- `settings.json`
- `CLAUDE.md`
- `skills/`
- `agents/`
- `commands/`
- `hooks/`
- `plugins/`
- `mcp/`
- `memory/`

## 置換しないもの

次のファイルやディレクトリは `~/.claude` で置き換えません。

- `.credentials.json`
- `history.jsonl` / `history/`
- `settings.local.json`
- `projects/`
- `todos/`
- `shell-snapshots/`
- `statsig/`
- `file-history/`
- `logs/`
- `ide/`
- `*.sqlite*` / `*.db`
- `cache/` / `.cache/`
- `tmp/` / `.tmp/`

## リポジトリ構造

- `toolbox/`: 初期状態へ戻すための Claude Code 設定原本。
- `toolbox-greece/`: 配布用 toolbox 第1号。
- `scripts/`: toolbox の複製、適用、確認を行うスクリプト。
- `tests/`: スクリプトの単体テスト。
- `docs/distribution/`: 配布用の運用文書。
- `docs/private/`: 個人研究用のローカル文書。Git では追跡しません。

詳細は [Repository Layout](docs/distribution/repository-layout.md) を参照してください。

## 開発と検証

開発依存は初回のみ入れます。

```bash
python3 -m pip install -e '.[dev]'
```

テストを実行します。

```bash
python3 -m pytest -q
```

## 安全メモ

- 実運用の `~/.claude` へ適用する前に、必ず `--dry-run` で確認する。
- 既存の `~/.claude` を変更する場合は、原則 `--safe` を使う。
- 認証情報や履歴を toolbox に含めない。
- 個人研究用の文書は `docs/private/` に置き、配布対象にしない。
