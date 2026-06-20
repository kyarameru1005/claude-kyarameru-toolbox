---
name: cerberus-permissions
description: リポジトリごとに Claude Code の権限を管理するため、リポジトリルートの `.claude/settings.json` を作成・更新し、allow / ask / deny の方針を一定に保つときに使う。権限の細分化、プロジェクト固有設定の分離、破壊的操作の遮断に向いている。
---

# cerberus-permissions

リポジトリ単位で実行を許す範囲を定め、リポジトリルートの `.claude/settings.json` に権限境界を集約するために使う。ユーザーが用途に応じて粒度を選べるよう、パターンの引き出しと分類基準を持つ。

## 重視すること

- 読み取りは粗く、書き込み・外向き・破壊操作は細かく分ける
- `deny` を最優先にして危険操作を確実に遮断する
- ユーザー共通・リポジトリ共有・個人ローカルの責務を混ぜない
- 秘密情報やマシン固有の値を設定に残さない
- 絞りすぎて作業が止まらないよう、allow は実運用で足す前提にする
- ユーザーが望む粒度（粗め / 標準 / 厳格）を確認し、過不足なく細分化する

## 重要な制約：settings.json はコメント不可

- `settings.json` は厳密な JSON で、`//` や `/* */` を書くと **設定全体が読み込めなくなる**。
- 日本語の説明を残したいときは、JSON にコメントを入れず次のいずれかにする。
  - 推奨：同じ `.claude/` に `PERMISSIONS.md` を置き、各ルールの意味・層・理由を日本語の対応表にする。
  - 補助：オブジェクト直下に `"_comment_*"` キーで要点だけ残す（配列の各行には付けられないので粒度は粗い）。
- どちらにするかはユーザーに確認する。既定は `PERMISSIONS.md` を併産する。
- 雛形は `templates/PERMISSIONS.md`（このスキル内）にある。これを `.claude/PERMISSIONS.md` へコピーし、リポジトリの実ルールに合わせて書き換える。

## 設定の層と優先順位

- `~/.claude/settings.json`: 全プロジェクト共通。最小限の安全策を置く。
- `.claude/settings.json`: リポジトリ共有。コミットする。プロジェクト固有の許可を置く。
- `.claude/settings.local.json`: 個人ローカル上書き。コミットしない（`.gitignore`）。
- 競合時の優先順位は local > リポジトリ > user。`deny` はどの層でも最優先。

## 粒度プリセット（ユーザーに選んでもらう）

- **粗め**: 読み取り・編集・検証まで広く allow、外向きと破壊のみ ask/deny。確認が少なく速い。
- **標準（既定）**: 読み取りは粗く、書き込みはコマンド単位、外向きは ask、破壊・秘密読取は deny。
- **厳格**: 編集もディレクトリ単位に限定し、`defaultMode` を絞る。確認は増えるが事故が起きにくい。

迷う場合は「標準」を提示し、外向き通信や編集範囲だけ個別に詰める。

## パターンの書き方

形式は「ツール → コマンド / サブコマンド → 引数」の順で、必要な分だけ細かくする。

- `Bash(git add:*)` … サブコマンド単位
- `Edit(plugins/**)` … 編集をディレクトリに限定
- `Read(./**/.env)` … パスのグロブ指定（`*` は1階層、`**` は再帰）
- `WebFetch(domain:example.com)` … 取得先ドメインの限定

### 引き出し（必要なものだけ採用）

- 読み取り: `Read`, `Grep`, `Glob`
- Git 参照: `Bash(git status:*)`, `Bash(git diff:*)`, `Bash(git log:*)`, `Bash(git branch:*)`, `Bash(git switch:*)`
- ステージ: `Bash(git add:*)`
- 検証 / テスト: プロジェクト固有のスクリプト（例 `Bash(python3 -m pytest:*)`）
- 編集の限定: `Edit(<対象ディレクトリ>/**)`（cwd 外編集を防ぐ）
- 外向き（ask 候補）: `Bash(git commit:*)`, `Bash(git push:*)`, `Bash(gh pr:*)`, `WebFetch`
- 破壊・履歴改変（deny 候補）: `Bash(git push --force:*)`, `Bash(git push -f:*)`, `Bash(git reset --hard:*)`, `Bash(git clean:*)`, `Bash(rm -rf:*)`
- 秘密情報（deny 候補）: `Read(./**/.env)`, `Read(./**/.env.*)`, `Read(./**/.credentials.json)`, `Read(./**/secrets/**)`
- 範囲外取得（deny 候補）: `Bash(curl:*)`, `Bash(wget:*)`（必要なら ask に緩める）

### 追加で使える設定

- `permissions.defaultMode`: 未列挙操作の既定（`acceptEdits` / `ask` など）。厳格にしたいとき検討。
- `permissions.additionalDirectories`: cwd 外で読み書きを許す追加ディレクトリ。安易に広げない。

## 手順

1. 既存の `~/.claude/settings.json` と `.claude/settings.json` を読み、現在の allow / ask / deny を把握する。
2. 望む粒度（粗め / 標準 / 厳格）と、日本語説明の持たせ方（`PERMISSIONS.md` / `_comment` / 両方）をユーザーに確認する。
3. このリポジトリ固有の操作（検証スクリプト、編集対象ディレクトリなど）を洗い出す。
4. 引き出しから必要なパターンを選び、読み取り→編集→検証→ステージを allow、commit / push / PR / 取得を ask、破壊・履歴改変・秘密読取を deny に分類する。
5. リポジトリ固有分を `.claude/settings.json` に書き、個人差は `.claude/settings.local.json` に分ける。
6. `PERMISSIONS.md` を用意する。新規なら `templates/PERMISSIONS.md` を `.claude/PERMISSIONS.md` にコピーし、リポジトリ名・粒度・最終更新・実ルールに合わせて書き換える。既存なら settings.json の差分に合わせて該当行を更新する（同期ずれを残さない）。
7. `.claude/settings.local.json` を `.gitignore` に入れる。
8. 変更後に JSON として読めること（`python3 -m json.tool` 等）と、想定する操作の許否を確認する。

## 判断基準

- 全プロジェクトで安全な禁止（`rm -rf`、force push など）は user 層に置く。
- このリポジトリでしか使わない許可（プロジェクト固有スクリプトなど）はリポジトリ層に置く。
- 環境依存や個人都合の緩和は local 層に置く。
- 編集を広く許すと cwd 外を触りうるため、必要なら `Edit(<dir>/**)` で対象を限定する。
- allow を細分化すると未列挙操作は ask（または `defaultMode`）に落ちる。最初は確認が増える前提で足していく。

## 注意

- `cwd` 外への設定変更や、既存 user 設定の破壊的な書き換えは事前確認する。
- 秘密情報、トークン、マシン固有パスを設定値に書かない。
- `settings.json` にコメントを書かない（読み込み不能になる）。説明は別ファイルへ。
- 広すぎる `deny` で必要な作業まで止めないか確認する。

## 出力

- 現在の権限構成の短い評価
- 選んだ粒度プリセットと、その理由
- 各層に置く allow / ask / deny の分類と理由
- 作成・更新する設定ファイル（`settings.json` と、必要なら `PERMISSIONS.md`）の最小差分
- コミット対象と `.gitignore` の扱い
- 確認した許否と残る注意点
