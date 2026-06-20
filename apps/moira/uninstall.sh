#!/bin/sh
# moira アンインストーラ（macOS / Linux）
#
# 使い方:
#   curl -fsSL https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/uninstall.sh | sh
#
# 環境変数:
#   BINDIR      インストール先（既定: $HOME/.local/bin）
#   MOIRA_SUDO  1 のとき、書き込み不可の場所の削除に sudo を使う（明示オプトイン）
set -eu

BINDIR="${BINDIR:-$HOME/.local/bin}"
target="$BINDIR/moira"

# 既定の場所に無ければ PATH 上から探す。
if [ ! -e "$target" ]; then
    found="$(command -v moira 2>/dev/null || true)"
    if [ -n "$found" ]; then
        target="$found"
    else
        echo "moira-uninstall: moira が見つかりません（BINDIR=$BINDIR）" >&2
        exit 1
    fi
fi

dir="$(dirname "$target")"
if [ -w "$dir" ]; then
    rm -f "$target"
elif [ "${MOIRA_SUDO:-}" = "1" ]; then
    echo "moira-uninstall: $target は書き込み不可。MOIRA_SUDO=1 のため sudo で削除します"
    sudo rm -f "$target"
else
    echo "moira-uninstall: $target を削除できません（書き込み不可）。sudo で消すなら MOIRA_SUDO=1 を付けて再実行してください" >&2
    exit 1
fi

echo "moira-uninstall: 削除しました -> $target"
echo "moira-uninstall: 各リポジトリの .ai/moira.json（タスク台帳）は残ります。必要なら手動で削除してください。"
