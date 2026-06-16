#!/bin/sh
# moira インストーラ（macOS / Linux）
#
# 使い方:
#   curl -fsSL https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.sh | sh
#
# 環境変数:
#   MOIRA_VERSION  インストールするタグ（既定: 最新リリース）
#   BINDIR         インストール先（既定: /usr/local/bin）
set -eu

REPO="kyarameru1005/claude-kyarameru-toolbox"
BINDIR="${BINDIR:-/usr/local/bin}"

err() {
    echo "moira-install: $*" >&2
    exit 1
}

# --- OS / arch から Rust ターゲットを判定 ---
os="$(uname -s)"
arch="$(uname -m)"
case "$os" in
    Darwin)
        case "$arch" in
            arm64 | aarch64) target="aarch64-apple-darwin" ;;
            x86_64) target="x86_64-apple-darwin" ;;
            *) err "未対応の arch: $arch" ;;
        esac
        ;;
    Linux)
        case "$arch" in
            x86_64 | amd64) target="x86_64-unknown-linux-gnu" ;;
            *) err "未対応の Linux arch: $arch（現状 x86_64 のみ対応）" ;;
        esac
        ;;
    *)
        err "未対応の OS: $os（Windows は install.ps1 を使用してください）"
        ;;
esac

# --- バージョン決定（既定は最新リリース）---
version="${MOIRA_VERSION:-}"
if [ -z "$version" ]; then
    version="$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | grep '"tag_name"' | head -n 1 \
        | sed -E 's/.*"tag_name": *"([^"]+)".*/\1/')"
    [ -n "$version" ] || err "最新リリースの取得に失敗（リポジトリが public か、リリースが存在するか確認）"
fi

asset="moira-${target}.tar.gz"
url="https://github.com/${REPO}/releases/download/${version}/${asset}"

# --- ダウンロード & 展開 ---
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
echo "moira-install: ${version} (${target}) を取得中..."
curl -fSL "$url" -o "$tmp/$asset" || err "ダウンロード失敗: $url"
tar -C "$tmp" -xzf "$tmp/$asset" || err "アーカイブの展開に失敗"
[ -f "$tmp/moira" ] || err "アーカイブに moira が含まれていない"
chmod +x "$tmp/moira"

# --- インストール（書き込めなければ sudo）---
mkdir -p "$BINDIR" 2>/dev/null || true
if [ -w "$BINDIR" ]; then
    mv "$tmp/moira" "$BINDIR/moira"
else
    echo "moira-install: $BINDIR は書き込み不可のため sudo を使用します"
    sudo mkdir -p "$BINDIR"
    sudo mv "$tmp/moira" "$BINDIR/moira"
fi

echo "moira-install: インストール完了 -> ${BINDIR}/moira"

# --- PATH 確認 ---
case ":$PATH:" in
    *":$BINDIR:"*) : ;;
    *) echo "moira-install: 注意: $BINDIR が PATH にありません。shell の設定に追加してください。" ;;
esac

"${BINDIR}/moira" --version || true
