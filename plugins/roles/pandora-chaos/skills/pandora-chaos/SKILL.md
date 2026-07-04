---
name: pandora-chaos
description: 障害を意図的に注入してシステムの耐障害性を検証する実験を設計し、コンテナ隔離環境でのみ安全に注入・観測・自動復旧まで行うときに使う。定常状態・仮説・爆発半径・観測・中断条件の整理と、管理された runner 経由の安全な実行に向いている。
---

# pandora-chaos

すぐ壊すことより、何を学ぶための実験かを先に決めることが重要なときに使う。
`aegis-review` がセキュリティ周辺の防御確認なのに対し、こちらは耐障害性（resilience）の検証実験を設計し、安全な範囲で実際に注入する。

## 対応サブエージェント

このスキルの役割は `khaos` サブエージェントとしても使える。文脈を分離したい／並行で回したいときは Task で `khaos` を起動し、インラインで足りるならそのまま進める。

## 重視すること

- 定常状態（steady-state）を観測可能な指標で定義する
- 1実験1仮説に絞る
- 最小の爆発半径（blast radius）から段階的に広げる
- 観測（メトリクス・ログ・トレース）と判定基準
- 中断条件（abort）とロールバック
- 非本番・コンテナ隔離・許可済みを前提にする

## 安全機構（仕組みで担保する）

注入の安全は「注意深さ」ではなく仕組みで守る。実行には runner（`templates/chaos-run.sh`）を使う。

- **コンテナガード**: コンテナ内でないと `--apply`（実注入）を拒否し、自動で dry-run になる。
- **時間制限＋自動ロールバック**: 障害は `DURATION` 秒後に必ず復旧。異常終了・中断（Ctrl-C）時も `trap` で復旧する。
- **opt-in / no-op**: 実験定義ファイルが無ければ何もしない。
- **dry-run 既定**: 既定は「やったつもり」表示。実注入は `--apply` を明示し、人間の承認を得てから行う。
- **依存ツール確認**: 必要コマンド（`tc`/`stress-ng` 等）が無ければ実行しない。

対応する障害モード: `process`（停止/再起動）・`resource`（CPU/メモリ枯渇）・`network`（遅延/パケットロス）・`dependency`（依存停止）。

## 使い方（runner）

```sh
# 雛形をリポジトリにコピー
cp "$CLAUDE_PLUGIN_ROOT/templates/chaos-run.sh"            .claude/chaos/chaos-run.sh
cp "$CLAUDE_PLUGIN_ROOT/templates/chaos-experiment.example.sh" .claude/chaos/my-exp.sh
chmod +x .claude/chaos/chaos-run.sh
# 実験定義(my-exp.sh)を編集してから、まず dry-run
.claude/chaos/chaos-run.sh .claude/chaos/my-exp.sh
# 内容を人間が承認したら、コンテナ隔離環境でのみ実注入
.claude/chaos/chaos-run.sh .claude/chaos/my-exp.sh --apply
```

## 手順

1. 対象と定常状態、観測する指標を決める。
2. 検証したい仮説を1つ立てる。
3. 最小の爆発半径で注入する障害モードを選び、実験定義に書く。
4. 中断条件とロールバック（時間制限）を用意する。
5. dry-run で内容を確認する。
6. 人間の承認を得てから、コンテナ隔離環境で `--apply` し、観測して自動復旧を確認する。
7. 結果から弱点と改善策をまとめる。

## 出力

- 実験計画（定常状態・仮説・障害モード・爆発半径）
- 観測指標と成功/失敗の判定基準
- 安全策（中断条件・ロールバック・前提）
- 実行記録（dry-run / 承認 / 実注入の可否）と観測結果・復旧確認
- わかった弱点と次の改善
