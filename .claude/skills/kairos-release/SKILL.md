---
name: kairos-release
description: この marketplace（claude-kyarameru-toolbox）の公開をバージョンで管理するときに使う。全 plugin.json と marketplace.json の version を semver で一括更新し、検証してリリース（コミット／タグ）まで整える手順。バージョン据え置きによる「更新が届かない」事故を防ぐ。
---

# kairos-release

この plugin marketplace を**バージョンで公開管理**するためのメンテナ向けスキル。
変更を出すたびに version を上げ、`/plugin marketplace update` で利用者へ確実に届くようにする。

## 前提（なぜ version を上げるのか）

- Claude Code は plugin の version を `plugin.json` の `version` から最優先で解決する。
- version 文字列が変わらないと「同一版」とみなされ、内容を変えても利用者に更新が届かない（キャッシュ据え置き）。
- このリポジトリは **全 plugin を同一 version で一括運用** する。`marketplace.json` の `metadata.version` も合わせる。

## semver の選び方

- **patch**（0.1.0 → 0.1.1）：既存 plugin の修正・文言・色など、後方互換の変更。
- **minor**（0.1.x → 0.2.0）：plugin / skill / agent の追加など、後方互換の機能追加。
- **major**（0.x → 1.0.0、1.x → 2.0.0）：破壊的変更（plugin 名の変更・削除、依存の非互換など）。

## 手順

1. 前回の公開（前 version / タグ）からの変更を `git log` / `git diff` で確認し、上の基準で **新 version** を決める。
2. 全 `plugins/**/.claude-plugin/plugin.json` の `version` を新 version に統一する。
3. `.claude-plugin/marketplace.json` の `metadata.version` も同じ新 version にする。
4. marketplace.json の各 entry には **個別 version を書かない**（`plugin.json` 側を真実にする。両方に書くと `plugin.json` が黙って優先され、ズレの原因になる）。
5. 検証する：
   - `python3 scripts/validate.py`
   - `python3 -m pytest -q`
   - `claude plugin validate .`（必要なら各 `plugins/*/*/` も）
6. 変更した plugin の README『動作確認シナリオ』を1件実行し、期待発火・要点どおりか確認する。
7. コミットする（`argo-git-flow` を使うと安全）。例: `plugins: バージョンを <new> へ更新`。
8. リリースを固定したい場合は **注釈付きタグ** を打つ。例:
   ```bash
   git tag -a v<new> -m "v<new>"
   git push origin v<new>
   ```
   タグ作成は破壊的でないが、push は外向き操作なので確認の上で行う。タグの強制移動はしない。
9. main へマージ後、利用者は `/plugin marketplace update kyarameru-claude` → `/reload-plugins` で新 version を受け取る。

## 一括更新の例（参考）

```python
from pathlib import Path
import json

NEW = "0.1.1"  # ← 決めた version に変える
for f in Path("plugins").glob("**/.claude-plugin/plugin.json"):
    d = json.loads(f.read_text(encoding="utf-8"))
    d["version"] = NEW
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
mk = Path(".claude-plugin/marketplace.json")
m = json.loads(mk.read_text(encoding="utf-8"))
m.setdefault("metadata", {})["version"] = NEW
mk.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("bumped to", NEW)
```

※ 隠しディレクトリ `.claude-plugin` を辿るため、`glob.glob("plugins/**/plugin.json")` は空振りする。
上記のように `.claude-plugin` を明示するか pathlib を使う。

## やらないこと

- version を据え置いたまま内容だけ変える（利用者に更新が届かない）。
- `plugin.json` と marketplace entry の両方に version を書く。
- 確認なしの force push、タグの強制移動。
- 一部 plugin だけ別 version にする（このリポジトリは一括運用。意図的に分けるとき以外は揃える）。

## 出力

- 決定した新 version と semver 区分（patch / minor / major）の理由
- 変更した plugin 数、`marketplace.json` の `metadata.version`
- 検証結果（validate.py / pytest / claude plugin validate）
- コミット内容、タグを打った場合はタグ名
- 利用者向けの更新手順（`marketplace update` → `reload-plugins`）
