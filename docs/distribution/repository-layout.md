# Repository Layout

この文書は、配布対象に含めるファイルと、個人用・実行時データとして配布しないファイルの置き場所を定義する。
使い方の入口は [README](../../README.md)、初回導入手順は [Getting Started](getting-started.md) を参照する。

## 基本方針

- `toolbox/` は初期状態へ戻すための最小 toolbox として保つ。
- `toolbox-greece/` は設定済み toolbox 第1号として配布する。
- 今後追加する `toolbox-名前/` は、配布用 toolbox として同じルールで管理する。
- `docs/distribution/` は配布相手が読む文書だけを置く。
- `docs/private/` は個人研究用のローカル文書を置く。Git では追跡しない。
- 認証情報、履歴、ログ、セッション、DB、キャッシュは配布しない。

## 主要ディレクトリ

- `toolbox/`: 初期状態へ戻すための Claude Code 設定原本。
- `toolbox-greece/`: 配布用 toolbox 第1号。Zeus などの役割別サブエージェントと作業スキルを含む。
- `toolbox-名前/`: 今後追加する配布用 toolbox。例: `toolbox-japan/`, `toolbox-work/`。
- `scripts/`: toolbox の複製、適用、状態確認を行うスクリプト。
- `tests/`: `scripts/` の単体テスト。
- `docs/distribution/`: 配布用の導入手順、構成説明、運用ルール。
- `docs/private/`: 個人研究用のメモやタスクリスト。`.gitignore` で除外する。

## 配布用ドキュメント

- `docs/distribution/getting-started.md`: 初めて toolbox を試す人向けの導入手順。
- `docs/distribution/repository-layout.md`: このファイル。リポジトリ構造と配布対象の説明。

## Toolbox の中身

`apply` が `~/.claude` で置き換える対象は次に限定する。
空ディレクトリ保持用の `.gitkeep` は置換対象に含めない。

- `settings.json`
- `CLAUDE.md`
- `skills/`
- `agents/`
- `commands/`
- `hooks/`
- `plugins/`
- `mcp/`
- `memory/`

## 配布しないもの

次のファイルやディレクトリは、`apply` でも `copy` でも管理対象から除外する。

- `.credentials.json`
- `history.jsonl` / `history/`
- `settings.local.json`
- `installation_id`
- `projects/`
- `todos/`
- `shell-snapshots/`
- `statsig/`
- `file-history/`
- `ide/`
- `logs/`
- `*.sqlite*` / `*.db`
- `cache/` / `.cache/`
- `tmp/` / `.tmp/`

## マニフェスト

`apply` 実行時は `~/.claude/.claude-kyarameru-toolbox-manifest.json` に管理対象だけを記録する。
このマニフェストは `toolbox-manager.py status` の確認材料として使う。

## 新しい toolbox を追加するとき

1. `python3 scripts/toolbox-manager.py copy --name <name>` で `toolbox-<name>/` を作る。
2. `toolbox-<name>/README.md` に目的、想定利用者、含めるエージェントやスキルを書く。
3. 認証情報、履歴、ログ、セッション、DB、キャッシュが入っていないことを確認する。
4. `python3 scripts/toolbox-manager.py apply --toolbox toolbox-<name> --dry-run` で置換予定を確認する。
5. 必要なら `README.md` とこの文書へ toolbox の位置づけを追記する。
