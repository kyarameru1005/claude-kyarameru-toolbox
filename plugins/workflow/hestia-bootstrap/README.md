# hestia-bootstrap

新しいリポジトリで Claude Code のハーネス一式を使い始めるとき、権限・品質ゲート・メモリ・Git 運用の初期セットアップを正しい順序で導入するために使う。設定の実体は持たず既存スキルへ委譲する。

## 動作確認シナリオ

- シナリオ: 新しいリポジトリで Claude Code のハーネス一式を使い始めたい。
- 入力例: 「このリポジトリに Claude Code のセットアップ一式を導入して」
- 期待する発火: `hestia-bootstrap` スキル。
- 期待する挙動の要点:
  - セットアップ正典の順序（CLAUDE.md → 権限 → 品質ゲート → moira → Git 運用）で進める。
  - 設定の実体は生成せず `cerberus-permissions`・`dike-gate`・`mnemosyne-memory`・`argo-git-flow` へ委譲する。
- 逸脱の例（NG）:
  - 設定ファイルの中身を自前で生成し、既存スキルと重複させる。
  - 順序を無視して個別スキルをばらばらに呼ぶ。
