# Getting Started

この手順は、配布された toolbox を安全に試すための最小手順です。
実際に `~/.claude` を置き換える前に、必ず dry-run で内容を確認します。

## 前提

- Python 3.11+
- このリポジトリを clone 済み
- Claude Code の設定ディレクトリとして `~/.claude` を使っている

## 1. 状態を確認する

```bash
python3 scripts/toolbox-manager.py status
```

`current`, `different`, `missing` が表示されます。
`different` は、対象の toolbox と現在の `~/.claude` が違う状態です。

## 2. 配布 toolbox を dry-run する

まずは `toolbox-greece/` を試します。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --dry-run
```

この時点ではファイルは変更されません。
表示された `Managed entries` と `Excluded entries` を確認します。

## 3. バックアップ付きで適用する

dry-run の内容に問題がなければ、`--safe` を使います。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox-greece --safe
```

既存の管理対象は `~/.claude/backup/<timestamp>/` に退避されます。

## 4. 初期状態へ戻す

設定を最小状態へ戻したい場合は、`toolbox/` を使います。

```bash
python3 scripts/toolbox-manager.py apply --toolbox toolbox --dry-run
python3 scripts/toolbox-manager.py apply --toolbox toolbox --safe
```

## 5. 新しい toolbox を作る

`toolbox/` から新しい配布用 toolbox を作れます。

```bash
python3 scripts/toolbox-manager.py copy --name japan
```

この例では `toolbox-japan/` が作られます。
認証情報、履歴、DB、ログ、セッション、キャッシュなどの除外対象は複製されません。

## 注意

- `--force` はバックアップなしで置換します。通常は使わないでください。
- `.credentials.json` や履歴ファイルは配布対象にしません。
- `settings.local.json`（ローカル個別設定）も配布対象にしません。
- 個人研究用のメモは `docs/private/` に置きます。このディレクトリは Git で追跡しません。
