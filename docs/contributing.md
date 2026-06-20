# 新しい plugin を追加する

このリポジトリは plugin marketplace です。新しいスキル/エージェントは plugin として追加します。

## 手順

1. **plugin ディレクトリを作る**: `plugins/<category>/<name>/`
   （`<category>` は `bundles`/`roles`/`workflow`/`design`、`<name>` は kebab-case・一意）。
   - スキル: `skills/<skill>/SKILL.md`（frontmatter に `description` 必須）。
   - エージェント: `agents/<agent>.md`（frontmatter に `name`/`description`/`tools`/`model`）。
2. **マニフェストを作る**: `plugins/<category>/<name>/.claude-plugin/plugin.json`。
   ```json
   { "name": "<name>", "version": "0.1.0", "description": "...",
     "author": { "name": "kyarameru" }, "dependencies": [] }
   ```
   共有したい基盤がある場合は `dependencies` にその plugin 名（同一 marketplace）を bare name で書く。
3. **README を置く**: `plugins/<category>/<name>/README.md`（目的・依存を簡潔に）。
4. **marketplace に登録する**: `.claude-plugin/marketplace.json` の `plugins` に追記。
   `source` は `./` 始まりのフルパス、`category` も付ける。
   ```json
   { "name": "<name>", "source": "./plugins/<category>/<name>",
     "description": "...", "category": "<category>" }
   ```
5. **検証する**:
   ```bash
   python3 scripts/validate.py
   python3 -m pytest -q
   claude plugin validate ./plugins/<category>/<name>   # 任意（ネイティブ検証）
   ```

## まとめパック（meta plugin）を作る場合

中身（skills/agents）を持たず、`plugin.json` の `dependencies` に束ねたい plugin を列挙するだけ。
`skills/` や `agents/` ディレクトリは不要です。

## 規約

- 絶対パスやマシン固有パス（`/Users/...`, `/home/...`）を書かない。ホーム参照は `~` / `$HOME`。
- 秘密情報をコミットしない。
- `name` はディレクトリ名・marketplace 掲載名・`plugin.json` の `name` をすべて一致させる。
- バージョンは当面リポジトリ一括で `0.1.0`。独立バージョニングが必要になったら
  `claude plugin tag` ＋ semver 制約へ移行する。
