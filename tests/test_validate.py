import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate.py"

AGENT = """---
name: {name}
description: テスト用エージェント。
tools: Read, Grep
model: opus
---

本文。
"""

SKILL = """---
name: {name}
description: テスト用スキル。
---

# {name}
"""


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def make_plugin(root: Path, name: str, *, skills=(), agents=(), dependencies=None, manifest_name=None):
    pdir = root / "plugins" / name
    manifest = {"name": manifest_name or name, "version": "0.1.0", "description": "x"}
    if dependencies:
        manifest["dependencies"] = list(dependencies)
    write(pdir / ".claude-plugin" / "plugin.json", json.dumps(manifest, ensure_ascii=False) + "\n")
    for s in skills:
        write(pdir / "skills" / s / "SKILL.md", SKILL.format(name=s))
    for a in agents:
        write(pdir / "agents" / f"{a}.md", AGENT.format(name=a))
    return pdir


def write_marketplace(root: Path, names, *, plugins=None):
    entries = plugins if plugins is not None else [
        {"name": n, "source": f"./plugins/{n}"} for n in names
    ]
    data = {
        "name": "kyarameru",
        "owner": {"name": "kyarameru"},
        "description": "テスト",
        "plugins": entries,
    }
    write(root / ".claude-plugin" / "marketplace.json", json.dumps(data, ensure_ascii=False) + "\n")


def run_in(tmp_path: Path):
    script = tmp_path / "scripts" / "validate.py"
    if not script.exists():
        write(script, SCRIPT.read_text(encoding="utf-8"))
    return subprocess.run([sys.executable, str(script)], text=True, capture_output=True)


def base(tmp_path: Path):
    """1 base plugin + 1 dependent plugin, all listed in marketplace."""
    make_plugin(tmp_path, "muse-interface", skills=["muse-interface"], agents=["aphrodite"])
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"], dependencies=["muse-interface"])
    write_marketplace(tmp_path, ["muse-interface", "muse-tech"])


def test_valid_marketplace_passes(tmp_path):
    base(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr
    assert "OK: marketplace + 2 plugins" in result.stdout


def test_missing_dependency_fails(tmp_path):
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"], dependencies=["muse-interface"])
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "dependencies の 'muse-interface' が存在しない" in result.stderr


def test_plugin_name_mismatch_fails(tmp_path):
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"], manifest_name="wrong")
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "一致しない" in result.stderr


def test_orphan_plugin_dir_fails(tmp_path):
    make_plugin(tmp_path, "muse-interface", skills=["muse-interface"])
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"], dependencies=["muse-interface"])
    write_marketplace(tmp_path, ["muse-interface"])  # muse-tech 未掲載
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "marketplace に未掲載" in result.stderr


def test_marketplace_entry_without_dir_fails(tmp_path):
    make_plugin(tmp_path, "muse-interface", skills=["muse-interface"])
    write_marketplace(tmp_path, ["muse-interface", "ghost"])  # ghost のディレクトリ無し
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "ghost" in result.stderr


def test_duplicate_marketplace_name_fails(tmp_path):
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    write_marketplace(
        tmp_path, [], plugins=[{"name": "muse-tech", "source": "./plugins/muse-tech"},
                               {"name": "muse-tech", "source": "./plugins/muse-tech"}]
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "重複" in result.stderr


def test_absolute_path_in_manifest_fails(tmp_path):
    base(tmp_path)
    manifest = tmp_path / "plugins" / "muse-tech" / ".claude-plugin" / "plugin.json"
    data = json.loads(manifest.read_text())
    data["description"] = "see /Users/me/secret"
    manifest.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "絶対パス" in result.stderr


def test_unknown_tool_in_agent_fails(tmp_path):
    base(tmp_path)
    agent = tmp_path / "plugins" / "muse-interface" / "agents" / "aphrodite.md"
    agent.write_text(
        "---\nname: aphrodite\ndescription: x\ntools: Read, Reed\nmodel: opus\n---\n",
        encoding="utf-8",
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "不明なツール 'Reed'" in result.stderr


def test_skill_missing_manifest_fails(tmp_path):
    base(tmp_path)
    (tmp_path / "plugins" / "muse-tech" / "skills" / "broken").mkdir(parents=True)
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "SKILL.md が無い" in result.stderr


def test_real_repo_is_valid():
    result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
