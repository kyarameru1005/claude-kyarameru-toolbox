import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "toolbox-manager.py"


def run_manager(tmp_path, *args, check=True):
    command = [
        sys.executable,
        str(SCRIPT),
        "--repo-root",
        str(tmp_path),
        *args,
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed: {command}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_copy_uses_next_available_toolbox_number(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "a"}\n')
    (tmp_path / "toolbox1").mkdir()

    result = run_manager(tmp_path, "copy")

    assert result.returncode == 0
    assert (tmp_path / "toolbox2" / "settings.json").read_text() == '{"model": "a"}\n'
    assert "Created toolbox2" in result.stdout


def test_copy_can_use_named_toolbox_destination(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "a"}\n')

    result = run_manager(tmp_path, "copy", "--name", "greece")

    assert result.returncode == 0
    assert (tmp_path / "toolbox-greece" / "settings.json").read_text() == '{"model": "a"}\n'
    assert "Created toolbox-greece" in result.stdout


def test_copy_excludes_runtime_and_secret_state(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "a"}\n')
    write(tmp_path / "toolbox" / ".credentials.json", "{}\n")
    write(tmp_path / "toolbox" / "history.jsonl", "{}\n")
    write(tmp_path / "toolbox" / "skills" / ".gitkeep", "")
    write(tmp_path / "toolbox" / "skills" / "demo" / "SKILL.md", "# Demo\n")
    write(tmp_path / "toolbox" / "skills" / "demo" / "state.sqlite", "db")
    write(tmp_path / "toolbox" / "projects" / "rollout.jsonl", "{}\n")
    write(tmp_path / "toolbox" / "cache" / "tool.json", "{}\n")

    run_manager(tmp_path, "copy", "--name", "greece")

    destination = tmp_path / "toolbox-greece"
    assert (destination / "settings.json").exists()
    assert (destination / "skills" / "demo" / "SKILL.md").exists()
    assert not (destination / "skills" / ".gitkeep").exists()
    assert not (destination / ".credentials.json").exists()
    assert not (destination / "history.jsonl").exists()
    assert not (destination / "skills" / "demo" / "state.sqlite").exists()
    assert not (destination / "projects").exists()
    assert not (destination / "cache").exists()


def test_apply_can_select_named_toolbox(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "base"}\n')
    write(tmp_path / "toolbox-greece" / "settings.json", '{"model": "two"}\n')
    claude_home = tmp_path / "claude-home"

    run_manager(
        tmp_path,
        "apply",
        "--toolbox",
        "toolbox-greece",
        "--claude-home",
        str(claude_home),
        "--yes",
        "--no-backup",
    )

    assert (claude_home / "settings.json").read_text() == '{"model": "two"}\n'


def test_apply_excludes_runtime_and_secret_state(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "base"}\n')
    write(tmp_path / "toolbox" / ".credentials.json", "{}\n")
    write(tmp_path / "toolbox" / "history.jsonl", "{}\n")
    write(tmp_path / "toolbox" / "skills" / ".gitkeep", "")
    write(tmp_path / "toolbox" / "skills" / "README.md", "# skills\n")
    write(tmp_path / "toolbox" / "skills" / "demo" / "SKILL.md", "# Demo\n")
    write(tmp_path / "toolbox" / "skills" / "demo" / "state.sqlite", "db")
    write(tmp_path / "toolbox" / "projects" / "rollout.jsonl", "{}\n")
    write(tmp_path / "toolbox" / "cache" / "tool.json", "{}\n")
    claude_home = tmp_path / "claude-home"

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--yes",
        "--no-backup",
    )

    assert (claude_home / "settings.json").exists()
    assert (claude_home / "skills").is_dir()
    assert (claude_home / "skills" / "demo" / "SKILL.md").exists()
    assert not (claude_home / "skills" / ".gitkeep").exists()
    assert not (claude_home / "skills" / "README.md").exists()
    assert not (claude_home / ".credentials.json").exists()
    assert not (claude_home / "history.jsonl").exists()
    assert not (claude_home / "skills" / "demo" / "state.sqlite").exists()
    assert not (claude_home / "projects").exists()
    assert not (claude_home / "cache").exists()


def test_apply_backs_up_overwritten_files(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "new"}\n')
    claude_home = tmp_path / "claude-home"
    write(claude_home / "settings.json", '{"model": "old"}\n')

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--yes",
        "--backup",
    )

    backups = list((claude_home / "backup").glob("*"))
    assert len(backups) == 1
    assert (backups[0] / "settings.json").read_text() == '{"model": "old"}\n'
    assert (claude_home / "settings.json").read_text() == '{"model": "new"}\n'


def test_apply_replaces_directory_contents_wholesale(tmp_path):
    write(tmp_path / "toolbox" / "skills" / "demo" / "SKILL.md", "# New\n")
    claude_home = tmp_path / "claude-home"
    write(claude_home / "skills" / "demo" / "SKILL.md", "# Old\n")
    write(claude_home / "skills" / "demo" / "legacy.txt", "stale\n")

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--yes",
        "--no-backup",
    )

    assert (claude_home / "skills" / "demo" / "SKILL.md").read_text() == "# New\n"
    assert not (claude_home / "skills" / "demo" / "legacy.txt").exists()


def test_safe_alias_backs_up_and_overwrites(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "new"}\n')
    claude_home = tmp_path / "claude-home"
    write(claude_home / "settings.json", '{"model": "old"}\n')

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--safe",
    )

    backups = list((claude_home / "backup").glob("*"))
    assert len(backups) == 1
    assert (backups[0] / "settings.json").read_text() == '{"model": "old"}\n'
    assert (claude_home / "settings.json").read_text() == '{"model": "new"}\n'


def test_force_alias_overwrites_without_backup(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "new"}\n')
    claude_home = tmp_path / "claude-home"
    write(claude_home / "settings.json", '{"model": "old"}\n')

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--force",
    )

    assert not (claude_home / "backup").exists()
    assert (claude_home / "settings.json").read_text() == '{"model": "new"}\n'


def test_dry_run_does_not_change_files(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "new"}\n')
    claude_home = tmp_path / "claude-home"
    write(claude_home / "settings.json", '{"model": "old"}\n')

    result = run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--dry-run",
    )

    assert result.returncode == 0
    assert (claude_home / "settings.json").read_text() == '{"model": "old"}\n'
    assert not (claude_home / ".claude-kyarameru-toolbox-manifest.json").exists()
    assert "Dry run: no files changed." in result.stdout


def test_noninteractive_overwrite_requires_explicit_yes(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "new"}\n')
    claude_home = tmp_path / "claude-home"
    write(claude_home / "settings.json", '{"model": "old"}\n')

    result = run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        check=False,
    )

    assert result.returncode != 0
    assert "Refusing to overwrite" in result.stderr
    assert (claude_home / "settings.json").read_text() == '{"model": "old"}\n'


def test_manifest_tracks_only_managed_entries(tmp_path):
    write(tmp_path / "toolbox" / "settings.json", '{"model": "base"}\n')
    write(tmp_path / "toolbox" / "skills" / "demo" / "SKILL.md", "# Demo\n")
    write(tmp_path / "toolbox" / ".credentials.json", "{}\n")
    claude_home = tmp_path / "claude-home"

    run_manager(
        tmp_path,
        "apply",
        "--claude-home",
        str(claude_home),
        "--yes",
        "--no-backup",
    )

    manifest = json.loads(
        (claude_home / ".claude-kyarameru-toolbox-manifest.json").read_text()
    )
    assert manifest["managed_by"] == "claude-kyarameru-toolbox"
    assert manifest["entries"] == ["settings.json", "skills"]


def _load_manager_module():
    """ハイフン入りファイル名のスクリプトをモジュールとして読み込む。"""
    import importlib.util

    spec = importlib.util.spec_from_file_location("toolbox_manager", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    # dataclass デコレータが cls.__module__ を解決できるよう先に登録する。
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _readme_managed_entries():
    """README の「## 置換対象」セクションに列挙された対象名を抜き出す。"""
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = text.split("## 置換対象", 1)[1].split("## 置換しないもの", 1)[0]
    entries = []
    for line in section.splitlines():
        line = line.strip()
        if line.startswith("- `") and line.endswith("`"):
            name = line[3:-1].rstrip("/")
            entries.append(name)
    return entries


def test_readme_matches_managed_entries():
    """置換対象の単一情報源化: MANAGED_ENTRIES と README 記載が一致する。"""
    module = _load_manager_module()
    assert sorted(_readme_managed_entries()) == sorted(module.MANAGED_ENTRIES)
