---
name: hestia-bootstrap
description: 新しいリポジトリで Claude Code のハーネス一式を使い始めるとき、権限・品質ゲート・メモリ・Git 運用の初期セットアップを正しい順序で導入するために使う。設定の実体・雛形は持たず既存スキルへ委譲し、重複を作らない。
---

# hestia-bootstrap

新しいリポジトリで Claude Code のハーネス一式を使い始めるときに使う。設定の実体や雛形は持たず、既存スキルへの委譲に徹する（実体を複製しない）。

## セットアップ正典（順序）

1. CLAUDE.md を最小で作成し、`mnemosyne-memory` でグローバルとの重複を除去する。
2. `cerberus-permissions` で `.claude/settings.json` と PERMISSIONS.md を用意する。
3. `dike-gate` で `.claude/quality-gate.sh` を設置し、実行権限を付ける（`chmod +x`）。
4. `moira init` でタスク台帳を作る（`moira` が無い環境ではスキップし、目的・現在地・次の一手を記すインラインのチェックリストで代替する）。
5. `argo-git-flow` で `claude/` ブランチ運用を確認し、`.gitignore` に `.ai/`・`settings.local.json` が入っているか確認する。

## やらないこと

- 設定の実体・雛形の複製
- 既存スキルが持つ手順の再定義

## 出力

- どのスキルへ委譲したか
- 完了した初期化ステップの一覧
