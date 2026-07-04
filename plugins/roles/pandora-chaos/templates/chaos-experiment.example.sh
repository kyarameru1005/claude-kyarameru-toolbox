#!/usr/bin/env bash
# pandora-chaos: 実験定義の雛形。
#
# 使い方:
#   cp "$CLAUDE_PLUGIN_ROOT/templates/chaos-experiment.example.sh" .claude/chaos/my-exp.sh
#   # 下を編集し、まず dry-run で内容を確認してから、コンテナ内で --apply する。
#
# 前提: コンテナ隔離・非本番環境でのみ実行する。本番を対象にしない。
# このファイルは chaos-run.sh から source される（変数を設定するだけ。直接実行しない）。
# shellcheck disable=SC2034  # 各変数は chaos-run.sh へ source され利用されるため、単体では未使用に見える

# ---- 共通 -----------------------------------------------------------------
# MODE: process | resource | network | dependency
MODE="process"

# DURATION: 障害を維持する秒数。経過後に必ず自動ロールバックされる。短く始める。
DURATION="20"

# 定常状態チェック: 正常なら exit 0 を返すコマンド。注入の前後に実行して比較する。
#   例: HTTP 200 を確認
# STEADY_STATE_CHECK='curl -fsS http://localhost:8080/health >/dev/null'
STEADY_STATE_CHECK=''

# 中断条件: 満たされたら exit 0 を返すコマンド。注入中に検出すると即ロールバックする。
#   例: エラーログが閾値を超えたら中断
# ABORT_CHECK='[ "$(wc -l < /var/log/app/error.log)" -gt 1000 ]'
ABORT_CHECK=''

# ---- mode=process : プロセス停止/再起動 -----------------------------------
# TARGET: pkill -f に渡すプロセス名/パターン。
TARGET="my-worker"
# RESTART_CMD: 復旧用コマンド（ロールバックで実行）。
RESTART_CMD="supervisorctl start my-worker"

# ---- mode=resource : CPU/メモリ枯渇（stress-ng 必須） ---------------------
# CPU_WORKERS="2"      # CPU を食うワーカ数
# MEM_BYTES="512M"     # 確保するメモリ量
# 復旧は自動（stress-ng プロセスを停止）。

# ---- mode=network : 遅延/パケットロス（tc・root/NET_ADMIN 必須） ----------
# IFACE="eth0"         # 対象インターフェース
# DELAY_MS="200"       # 付与する遅延(ms)
# LOSS_PCT="10"        # パケットロス率(%)
# 復旧は自動（tc qdisc del）。

# ---- mode=dependency : 依存サービス停止 -----------------------------------
# STOP_CMD="docker compose stop db"    # 依存を止める
# START_CMD="docker compose start db"  # 復旧で起動する
