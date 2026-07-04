#!/usr/bin/env bash
# pandora-chaos: 障害注入 runner（安全側）。
#
# 使い方:
#   cp "$CLAUDE_PLUGIN_ROOT/templates/chaos-run.sh" .claude/chaos/chaos-run.sh
#   cp "$CLAUDE_PLUGIN_ROOT/templates/chaos-experiment.example.sh" .claude/chaos/my-exp.sh
#   chmod +x .claude/chaos/chaos-run.sh
#   # まず dry-run（実際には何も起こさない）
#   .claude/chaos/chaos-run.sh .claude/chaos/my-exp.sh
#   # 人間が内容を承認したら、コンテナ隔離環境でのみ実注入
#   .claude/chaos/chaos-run.sh .claude/chaos/my-exp.sh --apply
#
# 安全設計（仕組みで担保する）:
#   1. コンテナガード … コンテナ内でないと --apply を拒否し dry-run に強制する。
#   2. 時間制限＋自動ロールバック … DURATION 秒後に必ず復旧。trap で異常終了/中断時も復旧する。
#   3. opt-in / no-op … 実験定義ファイルが無ければ何もしない。
#   4. dry-run 既定 … 既定は「やったつもり」表示。実注入は --apply を明示。
#   5. 依存ツール確認 … 必要コマンドが無ければ実行しない。
# 本番環境を対象にしないこと。許可された非本番・隔離環境でのみ使う。
set -euo pipefail

# ---- 引数 -----------------------------------------------------------------
EXPERIMENT="${1:-}"
MODE_FLAG="${2:-}"
APPLY=0
[ "$MODE_FLAG" = "--apply" ] && APPLY=1

log()  { printf '[chaos] %s\n' "$*" >&2; }
warn() { printf '[chaos][warn] %s\n' "$*" >&2; }
die()  { printf '[chaos][error] %s\n' "$*" >&2; exit 1; }

# ---- opt-in / no-op -------------------------------------------------------
if [ -z "$EXPERIMENT" ]; then
  log "実験定義ファイルが指定されていません（no-op）。使い方はこのファイル冒頭を参照。"
  exit 0
fi
if [ ! -f "$EXPERIMENT" ]; then
  log "実験定義 '$EXPERIMENT' がありません（no-op）。"
  exit 0
fi

# ---- コンテナガード -------------------------------------------------------
in_container() {
  [ -f /.dockerenv ] && return 0
  if grep -qaE 'docker|containerd|kubepods|lxc|podman' /proc/1/cgroup /proc/self/cgroup 2>/dev/null; then
    return 0
  fi
  [ "${CHAOS_FORCE_CONTAINER:-0}" = "1" ] && return 0  # テスト用の明示上書き
  return 1
}

if [ "$APPLY" = "1" ] && ! in_container; then
  warn "コンテナ隔離環境を検出できませんでした。--apply を無効化し dry-run に切り替えます。"
  warn "実注入はコンテナ内（/.dockerenv 等）でのみ許可されます。"
  APPLY=0
fi

# ---- 実験定義の読み込み ---------------------------------------------------
# 既定値。実験定義ファイル側で上書きする。
MODE=""
TARGET=""
DURATION="30"
DELAY_MS="200"
LOSS_PCT="10"
IFACE="eth0"
CPU_WORKERS="1"
MEM_BYTES="256M"
RESTART_CMD=""
STOP_CMD=""
START_CMD=""
STEADY_STATE_CHECK=""
ABORT_CHECK=""

# shellcheck disable=SC1090
source "$EXPERIMENT"

[ -n "$MODE" ] || die "実験定義に MODE がありません。"
case "$DURATION" in
  ''|*[!0-9]*) die "DURATION は正の整数（秒）で指定してください: '$DURATION'";;
esac
[ "$DURATION" -gt 0 ] || die "DURATION は 1 以上にしてください。"

have() { command -v "$1" >/dev/null 2>&1; }

# ---- 観測フック -----------------------------------------------------------
run_steady_state() {
  [ -n "$STEADY_STATE_CHECK" ] || { echo "(STEADY_STATE_CHECK 未設定)"; return 0; }
  if eval "$STEADY_STATE_CHECK"; then echo "OK"; else echo "NG"; fi
}

# 中断条件: 満たされたら 0 を返す（=即ロールバックすべき）。
abort_triggered() {
  [ -n "$ABORT_CHECK" ] || return 1
  eval "$ABORT_CHECK"
}

# ---- ロールバック（trap で必ず呼ばれる） ---------------------------------
ROLLED_BACK=0
ROLLBACK_RESULT="(未実行)"
rollback() {
  [ "$ROLLED_BACK" = "1" ] && return 0
  ROLLED_BACK=1
  if [ "$APPLY" != "1" ]; then
    ROLLBACK_RESULT="(dry-run: 復旧コマンドは実行しません)"
    return 0
  fi
  log "ロールバックを実行します（mode=${MODE}）。"
  case "$MODE" in
    process)    [ -n "$RESTART_CMD" ] && eval "$RESTART_CMD" || true ;;
    resource)   pkill -P $$ stress-ng 2>/dev/null || true
                [ -n "${_RES_PIDS:-}" ] && kill "$_RES_PIDS" 2>/dev/null || true ;;
    network)    tc qdisc del dev "$IFACE" root 2>/dev/null || true ;;
    dependency) [ -n "$START_CMD" ] && eval "$START_CMD" || true ;;
  esac
  ROLLBACK_RESULT="完了"
  log "ロールバック完了。"
}
trap rollback EXIT INT TERM

# ---- 障害注入（モード別） -------------------------------------------------
DRY="[dry-run] "
[ "$APPLY" = "1" ] && DRY=""

inject() {
  case "$MODE" in
    process)
      [ -n "$TARGET" ] || die "process モードには TARGET（プロセス名/パターン）が必要です。"
      log "${DRY}プロセス停止: pkill -f '$TARGET'（復旧: ${RESTART_CMD:-なし}）"
      [ "$APPLY" = "1" ] && pkill -f "$TARGET" || true
      ;;
    resource)
      have stress-ng || { warn "stress-ng が無いため resource モードを実行できません（no-op）。"; return 0; }
      log "${DRY}リソース圧迫: stress-ng --cpu $CPU_WORKERS --vm 1 --vm-bytes $MEM_BYTES --timeout ${DURATION}s"
      if [ "$APPLY" = "1" ]; then
        stress-ng --cpu "$CPU_WORKERS" --vm 1 --vm-bytes "$MEM_BYTES" --timeout "${DURATION}s" &
        _RES_PIDS="$!"
      fi
      ;;
    network)
      have tc || { warn "tc(iproute2) が無いため network モードを実行できません（no-op）。"; return 0; }
      if [ "$APPLY" = "1" ] && [ "$(id -u)" != "0" ]; then
        warn "network モードは root/NET_ADMIN が必要です。実行をスキップします（no-op）。"; APPLY=0; DRY="[dry-run] "
      fi
      log "${DRY}ネットワーク障害: tc qdisc add dev $IFACE root netem delay ${DELAY_MS}ms loss ${LOSS_PCT}%"
      [ "$APPLY" = "1" ] && tc qdisc add dev "$IFACE" root netem delay "${DELAY_MS}ms" loss "${LOSS_PCT}%"
      ;;
    dependency)
      [ -n "$STOP_CMD" ] || die "dependency モードには STOP_CMD が必要です。"
      log "${DRY}依存停止: ${STOP_CMD}（復旧: ${START_CMD:-なし}）"
      [ "$APPLY" = "1" ] && eval "$STOP_CMD" || true
      ;;
    *)
      die "未知の MODE: '$MODE'（process|resource|network|dependency）"
      ;;
  esac
}

# ---- 実行フロー -----------------------------------------------------------
log "実験: $EXPERIMENT / mode=$MODE / duration=${DURATION}s / $([ "$APPLY" = 1 ] && echo APPLY || echo DRY-RUN)"
BEFORE="$(run_steady_state)"
log "定常状態(before): $BEFORE"

inject

# 注入を DURATION 秒維持。中断条件を毎秒監視し、満たされたら早期ロールバック。
ABORTED=0
if [ "$APPLY" = "1" ]; then
  elapsed=0
  while [ "$elapsed" -lt "$DURATION" ]; do
    if abort_triggered; then warn "中断条件を検出。早期ロールバックします。"; ABORTED=1; break; fi
    sleep 1; elapsed=$((elapsed + 1))
  done
else
  log "[dry-run] ${DURATION}s 待機・監視は省略します。"
fi

rollback
AFTER="$(run_steady_state)"

# ---- レポート -------------------------------------------------------------
cat >&2 <<EOF

===== chaos レポート =====
実験           : $EXPERIMENT
モード         : $MODE  (target=${TARGET:-n/a})
実行種別       : $([ "$APPLY" = "1" ] && echo "APPLY（実注入）" || echo "DRY-RUN（無害）")
継続時間       : ${DURATION}s
定常状態 before: $BEFORE
定常状態 after : $AFTER
中断条件       : $([ "$ABORTED" = "1" ] && echo "発火（早期中断）" || echo "未発火")
ロールバック   : $ROLLBACK_RESULT
==========================
EOF
