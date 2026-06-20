---
name: dike-gate
description: コミット直前と作業終了時に品質チェック（lint・テスト・検証）を強制したいときに使う。各リポジトリの .claude/quality-gate.sh を hooks で実行し、失敗すればコミットや終了をブロックする。スキップさせない品質ゲートの設計・運用に向いている。
---

# dike-gate

コミット直前と作業終了時に品質チェックを強制したいときに使う。各リポジトリの `.claude/quality-gate.sh` を hooks で実行し、失敗すればコミットや終了をブロックする。

## 仕組み（二層）

- ハード強制: plugin 同梱の hooks が `PreToolUse(git commit)` と `Stop` で `.claude/quality-gate.sh` を実行する。失敗ならブロック、未設置なら素通り（no-op）。
- 補助: このスキルがセットアップと運用方針を示す（強制は hooks 側が担う）。

## セットアップ

1. 雛形をコピー: `cp "$CLAUDE_PLUGIN_ROOT/templates/quality-gate.sh" .claude/quality-gate.sh`
2. 実行権限を付ける: `chmod +x .claude/quality-gate.sh`
3. 中身を定義する（Tier1＝速い・決定的）。lint → 高速テスト → 構造検証 の順に並べ、失敗は非0終了にする。

## 重視すること

- 速いものを手前に置く。コミット時の関門は lint・軽い単体に絞り、重いもの（全テスト・カバレッジ・SAST/SCA・E2E）は CI／リリース前へ回す。
- 決定的・冪等にする。flaky・ネット依存・環境依存のチェックは関門にしない。
- hooks はローカルの速い関門、CI は確実な関門。両方を併用する。
- ゲートはスキップさせない。失敗したら直してから再コミット／再終了する。

## 手順

1. `.claude/quality-gate.sh` を用意する（上記セットアップ）。
2. コミットや作業終了のたびに hooks が自動実行する（手動操作は不要）。
3. 失敗したら返されたログで原因を直し、再試行する。

## 出力

- セットアップ済みの `.claude/quality-gate.sh`
- ゲートで実行するチェックの一覧と段階（Tier1 / CI / リリース前）
- 失敗時の原因と修正方針
