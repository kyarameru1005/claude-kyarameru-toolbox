# Changelog

このリポジトリの公開バージョン（全 plugin と `marketplace.json` の `metadata.version` を
一括運用、[kairos-release](.claude/skills/kairos-release/SKILL.md) 参照）ごとの変更点。

## v0.5.0 (2026-07-04)

- 追加: `roles/panacea-debug`（agent: asclepius）。再現手順の固定→一変数ずつの切り分け→
  二分探索→根本原因特定でバグを直すデバッグ専用の役割。修正実装は行わず hephaestus へ委譲する。
- 追加: `workflow/hestia-bootstrap`。新規リポジトリでハーネス一式を使い始める導線
  （CLAUDE.md → 権限 → 品質ゲート → moira → Git 運用の正典順序）。設定の実体は持たず
  既存スキルへ委譲する。
- 追加: 主要 plugin の README に「動作確認シナリオ」節、シナリオ記載名の実在を守る
  自動テスト、`kairos-release` 手順へのシナリオ実行確認ステップ。

## v0.4.1 (2026-07-04)

- 修正: `dike-gate` の `hooks.json` にあった無効な `"if"` フィールド（Claude Code の
  hooks スキーマに存在せず無視される）が原因で、品質ゲートが全 Bash コマンドで
  発火していた不具合を修正。`run-gate.sh` 側で `git commit` を含むコマンドのみ
  ゲートを実行するよう変更。

## v0.4.0 (2026-06-25)

- 追加: `pandora-chaos` にコンテナ隔離前提の安全な障害注入（`chaos-run.sh`）。
- 追加: `greece-roles` バンドルに `dike-gate` を依存として追加。

## v0.3.0 (2026-06-20)

- 追加: 品質ゲート plugin `dike-gate`（`git commit` 直前・作業終了時に
  `.claude/quality-gate.sh` を実行するフック）。

## v0.2.1 (2026-06-20)

- 整理: role 系 plugin の skill/agent 定義を整合化し、olympus のスキルを簡潔化。

## v0.2.0 (2026-06-20)

- 変更: `zeus-orchestrate` を `olympus-orchestrate` へ改名。

## v0.1.1 (2026-06-20)

- 修正: 初期リリース後の軽微な修正。

## v0.1.0 (2026-06-16)

- 初回リリース。役割別サブエージェント（Zeus 入口の greece-roles）と
  デザイン系統スキル（muse-*）を plugin marketplace として公開。
