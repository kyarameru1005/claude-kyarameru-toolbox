# skills

このディレクトリは、`toolbox-greece` で使うスキルを置く場所です。
ここでいうスキルは、サブエージェントそのものではなく、「どう進めるか」の作業パターンです。

この toolbox では、次のように役割を分けます。

- エージェント名: 神名（`agents/*.md`）
- スキル名: 神話の道具・場所・概念（`skills/*/SKILL.md`）

つまり、

- `zeus` や `hermes` は「誰が担当するか」
- `aegis-review` や `labyrinth-explore` は「どの型で進めるか」

を表します。

多くは agent と skill の並行ペアですが、全てが1対1ではありません。
`ares`（セキュリティ）と `chronos`（記録・振り返り）は専用 skill を持たず、
それぞれ `aegis-review` / `chronicle-docs` で兼ねる例外です。

## スキル一覧

- `zeus-orchestrate`: オーケストレーション発火。役割分担と進行計画を明示する。
- `labyrinth-explore`: 事前調査。関連ファイル・処理フロー・影響範囲を整理する。
- `oracle-design`: 設計判断。構造・責務分離・選択肢比較を行う。
- `muse-interface`: UI/ビジュアル設計の親スキル。レイアウト・視覚階層・状態・一貫性を決める。
- `muse-modern`: デザイン系統（モダン）。クリーン・フラット・余白多めのトーン。
- `muse-luxury`: デザイン系統（高級感）。深色・金属アクセント・静けさのトーン。
- `muse-minimal`: デザイン系統（シンプル/ミニマル）。引き算・モノクローム寄りのトーン。
- `muse-bold`: デザイン系統（かっこいい/大胆）。高コントラスト・太いタイポのトーン。
- `muse-avantgarde`: デザイン系統（最先端）。先鋭・実験的な表現のトーン。
- `forge-implement`: 実装。最小差分で安全に変更する。
- `aegis-review`: レビュー。バグ・回帰・危険な仮定・保守性リスクを洗い出す。
- `gauntlet-verify`: 検証。テスト・チェック結果を pass / fail / 未確認 で整理する。
- `pandora-chaos`: 耐障害性検証。障害注入実験の定常状態・仮説・爆発半径・安全策を設計する。
- `chronicle-docs`: 文書化。README・設計メモ・記録を再利用しやすくまとめる。
- `argo-git-flow`: Git 作業フロー。ブランチ・コミット・プッシュ・PR を安全に進める。
- `atlas-repository`: リポジトリ構造整理。配置・命名・境界を一定に保つ。
- `cerberus-permissions`: 権限管理。リポジトリルートの `.claude/settings.json` で allow / ask / deny を定める。

## 基本の使い分け

迷ったときは、次の流れで考えると分かりやすいです。

1. まず調査が必要かを判断する
2. 設計判断が必要なら実装前に止まる
3. 実装後はレビューか検証を入れる
4. 説明が必要なら最後に文書化する

対応関係は次のとおりです。

- 調査: `labyrinth-explore`
- 設計: `oracle-design`
- UI/ビジュアル設計: `muse-interface`（親） + 見た目の系統スキル
- 実装: `forge-implement`
- レビュー: `aegis-review`
- 検証: `gauntlet-verify`
- 耐障害性検証: `pandora-chaos`
- 文書化: `chronicle-docs`
- Git 作業: `argo-git-flow`
- リポジトリ整理: `atlas-repository`
- 権限管理: `cerberus-permissions`
- オーケストレーション: `zeus-orchestrate`

## 典型的な組み合わせ

### 小さい修正

- `zeus` → `forge-implement` → `aegis-review` または `gauntlet-verify`

### 影響範囲が不明な修正

- `zeus` → `labyrinth-explore` → `forge-implement` → `gauntlet-verify`

### 設計判断を含む修正

- `zeus` → `labyrinth-explore` → `oracle-design` → `forge-implement` → `aegis-review` → `gauntlet-verify`

### 文書中心の作業

- `zeus` → `chronicle-docs`

### UI/ビジュアル設計

- `muse-interface`（共通の UI 構造）で土台を決め、見た目の系統スキルを併用する。
- 例: `muse-interface` + `muse-luxury`（高級感に寄せる場合）

## デザイン系統スキル（`muse-*`）

UI/ビジュアル設計は「共通の構造」と「見た目のトーン」を分けて扱います。

- 親（共通の構造）: `muse-interface`
  - レイアウト・情報設計・状態表現・一貫性・アクセシビリティを決める。
- 系統（見た目のトーン）: `muse-modern` / `muse-luxury` / `muse-minimal` / `muse-bold` / `muse-avantgarde`
  - 配色・タイポ・余白・装飾・モーションの方向を系統ごとに与える。

使うときは「親で構造を決め、系統で見た目を寄せる」の順で組み合わせます。
系統は基本どれか1つを選び、混在させないことで一貫性を保ちます。

## 命名ルール

この toolbox では、世界観を壊さないためにスキル名を神話の道具・場所・概念で統一します。
ただし、名前だけで意味が分からなくならないよう、神話語 + 実務語の形を保ちます。

例: `aegis-review`, `labyrinth-explore`, `forge-implement`, `zeus-orchestrate`

同じ系統のスキル群は共通の接頭辞でまとめます。
例: UI/ビジュアル設計の `muse-*`（`muse-interface`, `muse-modern`, `muse-luxury` …）。

## 追加するときの基準

新しいスキルを増やす前に、まず次を確認します。

- 既存スキルのどれでも代用できないか
- 新しいスキルに独立した作業パターンがあるか
- 名前だけで役割をある程度推測できるか

スキルは増やしすぎると使い分けが難しくなるので、最小セットを保つ方が運用しやすいです。
