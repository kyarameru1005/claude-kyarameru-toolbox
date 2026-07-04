"""dike-gate の run-gate.sh を実際に実行して回帰を防ぐ。

過去に fail-open（git commit を素通りさせてしまう）の regex 不具合があったため
（see: PR #44）、実際の見逃しケースを固定テストにする。
"""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_GATE = REPO_ROOT / "plugins" / "workflow" / "dike-gate" / "hooks" / "run-gate.sh"

if sys.platform.startswith("win"):
    import pytest

    pytest.skip("run-gate.sh は POSIX シェル専用", allow_module_level=True)


def make_gate(tmp_path: Path, *, exit_code: int, marker: bool = True) -> None:
    gate = tmp_path / ".claude" / "quality-gate.sh"
    gate.parent.mkdir(parents=True, exist_ok=True)
    marker_line = f': > "{tmp_path}/ran.marker"\n' if marker else ""
    gate.write_text(
        f"#!/usr/bin/env bash\n{marker_line}echo GATE-OUTPUT\nexit {exit_code}\n",
        encoding="utf-8",
    )
    gate.chmod(0o755)


def run_hook(tmp_path: Path, event: str, command: str | None = None) -> subprocess.CompletedProcess:
    payload: dict = {"hook_event_name": event}
    if command is not None:
        payload["tool_input"] = {"command": command}
    env = {"CLAUDE_PROJECT_DIR": str(tmp_path), "PATH": "/usr/bin:/bin:/usr/local/bin"}
    return subprocess.run(
        ["bash", str(RUN_GATE)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        env=env,
    )


def gate_ran(tmp_path: Path) -> bool:
    return (tmp_path / "ran.marker").exists()


def test_gate_not_installed_is_noop(tmp_path: Path):
    result = run_hook(tmp_path, "PreToolUse", "git commit -m x")
    assert result.returncode == 0
    assert result.stdout == ""
    assert not gate_ran(tmp_path)


def test_non_commit_command_skips_gate(tmp_path: Path):
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "PreToolUse", "ls -la")
    assert result.returncode == 0
    assert not gate_ran(tmp_path)


def test_plain_git_commit_runs_gate(tmp_path: Path):
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "PreToolUse", 'git commit -m "x"')
    assert result.returncode == 0
    assert gate_ran(tmp_path)


def test_compound_command_with_commit_runs_gate(tmp_path: Path):
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "PreToolUse", "git add -A && git commit -m x")
    assert result.returncode == 0
    assert gate_ran(tmp_path)


def test_git_dash_c_option_runs_gate(tmp_path: Path):
    # 過去の fail-open regression: git -C/-c はオプションの引数がハイフン始まりで
    # ないため、旧 regex では見逃していた。
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "PreToolUse", "git -C sub commit")
    assert result.returncode == 0
    assert gate_ran(tmp_path)


def test_absolute_path_git_runs_gate(tmp_path: Path):
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "PreToolUse", "/usr/bin/git commit")
    assert result.returncode == 0
    assert gate_ran(tmp_path)


def test_gate_failure_on_pretooluse_emits_deny_json(tmp_path: Path):
    make_gate(tmp_path, exit_code=1)
    result = run_hook(tmp_path, "PreToolUse", "git commit -m x")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "GATE-OUTPUT" in data["hookSpecificOutput"]["additionalContext"]


def test_gate_failure_on_stop_emits_block_json(tmp_path: Path):
    make_gate(tmp_path, exit_code=1)
    result = run_hook(tmp_path, "Stop")
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["decision"] == "block"
    assert "GATE-OUTPUT" in data["hookSpecificOutput"]["additionalContext"]


def test_stop_event_always_runs_gate_even_without_commit(tmp_path: Path):
    make_gate(tmp_path, exit_code=0)
    result = run_hook(tmp_path, "Stop")
    assert result.returncode == 0
    assert gate_ran(tmp_path)
