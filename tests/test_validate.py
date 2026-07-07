import json
import re
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


def make_plugin(
    root: Path,
    name: str,
    *,
    skills=(),
    agents=(),
    dependencies=None,
    manifest_name=None,
    version="0.1.0",
):
    pdir = root / "plugins" / name
    manifest = {"name": manifest_name or name, "version": version, "description": "x"}
    if dependencies:
        manifest["dependencies"] = list(dependencies)
    write(pdir / ".claude-plugin" / "plugin.json", json.dumps(manifest, ensure_ascii=False) + "\n")
    for s in skills:
        write(pdir / "skills" / s / "SKILL.md", SKILL.format(name=s))
    for a in agents:
        write(pdir / "agents" / f"{a}.md", AGENT.format(name=a))
    return pdir


def write_marketplace(root: Path, names, *, plugins=None, metadata=None):
    entries = (
        plugins if plugins is not None else [{"name": n, "source": f"./plugins/{n}"} for n in names]
    )
    data = {
        "name": "kyarameru",
        "owner": {"name": "kyarameru"},
        "description": "テスト",
        "plugins": entries,
    }
    if metadata is not None:
        data["metadata"] = metadata
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
        tmp_path,
        [],
        plugins=[
            {"name": "muse-tech", "source": "./plugins/muse-tech"},
            {"name": "muse-tech", "source": "./plugins/muse-tech"},
        ],
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "重複" in result.stderr


def test_absolute_path_in_manifest_fails(tmp_path):
    base(tmp_path)
    manifest = tmp_path / "plugins" / "muse-tech" / ".claude-plugin" / "plugin.json"
    data = json.loads(manifest.read_text())
    # 連結で組み立てる（リテラルだとこのテストファイル自身が追跡ファイル走査に検出される）
    data["description"] = "see " + "/Users/" + "me/secret"
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


def test_mismatched_plugin_versions_fail(tmp_path):
    make_plugin(tmp_path, "muse-interface", skills=["muse-interface"], version="0.1.0")
    make_plugin(
        tmp_path,
        "muse-tech",
        skills=["muse-tech"],
        dependencies=["muse-interface"],
        version="0.2.0",
    )
    write_marketplace(tmp_path, ["muse-interface", "muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "version が揃っていない" in result.stderr


def test_metadata_version_mismatch_fails(tmp_path):
    base(tmp_path)  # all plugins 0.1.0
    write_marketplace(tmp_path, ["muse-interface", "muse-tech"], metadata={"version": "0.9.9"})
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "metadata.version" in result.stderr


def test_entry_level_version_fails(tmp_path):
    make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    write_marketplace(
        tmp_path,
        [],
        plugins=[{"name": "muse-tech", "source": "./plugins/muse-tech", "version": "0.1.0"}],
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "marketplace entry に version を書かない" in result.stderr


def test_real_repo_is_valid():
    result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr


def test_invalid_json_in_manifest_fails(tmp_path):
    base(tmp_path)
    manifest = tmp_path / "plugins" / "muse-tech" / ".claude-plugin" / "plugin.json"
    manifest.write_text("{ not valid json", encoding="utf-8")
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "JSON として不正" in result.stderr


def test_non_kebab_plugin_name_fails(tmp_path):
    make_plugin(tmp_path, "BadName", skills=["x"])
    write_marketplace(tmp_path, ["BadName"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "kebab-case でない" in result.stderr


def test_agent_missing_required_key_fails(tmp_path):
    base(tmp_path)
    agent = tmp_path / "plugins" / "muse-interface" / "agents" / "aphrodite.md"
    # model キーを欠落させる
    agent.write_text(
        "---\nname: aphrodite\ndescription: x\ntools: Read\n---\n",
        encoding="utf-8",
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "必須キー 'model' が無い" in result.stderr


# --- 追跡ファイル走査（絶対パス・秘密情報・.env） ---------------------------
# 検出対象の文字列は連結で組み立てる（リテラルだとこのテストファイル自身が
# 実リポジトリの走査に検出されるため）。


def git_track(tmp_path: Path) -> None:
    """tmp_path を git リポジトリ化し全ファイルをステージする（ls-files 対象化）。"""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, capture_output=True)


def test_untracked_repo_skips_file_scan(tmp_path):
    # git リポジトリでなければ走査は no-op（既存の検証だけで通る）
    base(tmp_path)
    write(tmp_path / "docs" / "note.md", "log: " + "/Users/" + "tester/tool\n")
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_tracked_machine_path_fails(tmp_path):
    base(tmp_path)
    write(tmp_path / "docs" / "note.md", "log: " + "/Users/" + "tester/tool\n")
    git_track(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "docs/note.md:1" in result.stderr
    assert "絶対パス" in result.stderr


def test_path_example_placeholder_ok(tmp_path):
    # ドキュメントの例示（/Users/... の形）はユーザー名が無いため許容される
    base(tmp_path)
    write(tmp_path / "docs" / "note.md", "絶対パス（" + "/Users/" + "... など）を書かない\n")
    git_track(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_tracked_secret_fails_without_echoing_value(tmp_path):
    base(tmp_path)
    fake_key = "sk-ant-" + "a" * 24
    write(tmp_path / "docs" / "note.md", f"key = {fake_key}\n")
    git_track(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "docs/note.md:1" in result.stderr
    assert "Anthropic API キー" in result.stderr
    assert fake_key not in result.stderr  # 値そのものをログに出さない


def test_tracked_env_file_fails(tmp_path):
    base(tmp_path)
    write(tmp_path / ".env", "TOKEN=x\n")
    git_track(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert ".env が追跡されている" in result.stderr


def test_env_example_ok(tmp_path):
    base(tmp_path)
    write(tmp_path / ".env.example", "TOKEN=\n")
    git_track(tmp_path)
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_agent_invalid_model_fails(tmp_path):
    base(tmp_path)
    agent = tmp_path / "plugins" / "muse-interface" / "agents" / "aphrodite.md"
    agent.write_text(
        "---\nname: aphrodite\ndescription: x\ntools: Read\nmodel: gpt-4\n---\n",
        encoding="utf-8",
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "model 'gpt-4' が不正" in result.stderr


def test_claude_prefixed_model_is_allowed(tmp_path):
    base(tmp_path)
    agent = tmp_path / "plugins" / "muse-interface" / "agents" / "aphrodite.md"
    agent.write_text(
        "---\nname: aphrodite\ndescription: x\ntools: Read\nmodel: claude-opus-4-8\n---\n",
        encoding="utf-8",
    )
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_mcp_tool_is_allowed(tmp_path):
    base(tmp_path)
    agent = tmp_path / "plugins" / "muse-interface" / "agents" / "aphrodite.md"
    agent.write_text(
        "---\nname: aphrodite\ndescription: x\ntools: Read, mcp__foo__bar\nmodel: opus\n---\n",
        encoding="utf-8",
    )
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_source_dir_name_mismatch_fails(tmp_path):
    base(tmp_path)
    write_marketplace(
        tmp_path,
        [],
        plugins=[
            {"name": "muse-interface", "source": "./plugins/muse-interface"},
            {"name": "muse-tech", "source": "./plugins/muse-interface"},
        ],
    )
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "source ディレクトリ名" in result.stderr


def test_readme_scenario_names_exist_in_real_repo():
    """README の『動作確認シナリオ』にある期待する発火先が実在することを確認する。

    kairos-release 手順6 はシナリオ実行を前提にするため、リネームで
    シナリオ記載が静かに壊れるのを防ぐ。
    """
    readmes = sorted((REPO_ROOT / "plugins").glob("*/*/README.md"))

    skill_names = {p.name for p in REPO_ROOT.glob("plugins/*/*/skills/*") if p.is_dir()}
    agent_names = {p.stem for p in REPO_ROOT.glob("plugins/*/*/agents/*.md")}
    plugin_names = {p.name for p in REPO_ROOT.glob("plugins/*/*") if p.is_dir()}
    known_names = skill_names | agent_names | plugin_names

    scenario_readmes = []
    missing = []
    for readme in readmes:
        text = readme.read_text(encoding="utf-8")
        if "動作確認シナリオ" not in text:
            continue
        scenario_readmes.append(readme)
        for line in text.splitlines():
            if "期待する発火" not in line:
                continue
            for name in re.findall(r"`([a-z0-9-]+)`", line):
                if name not in known_names:
                    missing.append(f"{readme.relative_to(REPO_ROOT)}: '{name}'")

    assert scenario_readmes, "『動作確認シナリオ』節を持つ README が見つからない"
    assert not missing, "存在しない skill/agent/plugin 名が記載されている:\n" + "\n".join(missing)


def test_marketplace_missing_owner_fails(tmp_path):
    base(tmp_path)
    mk = tmp_path / ".claude-plugin" / "marketplace.json"
    data = json.loads(mk.read_text())
    del data["owner"]
    mk.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "必須キー 'owner' が無い" in result.stderr


VALID_HOOKS = {
    "hooks": {
        "PreToolUse": [
            {
                "matcher": "Bash",
                "hooks": [
                    {
                        "type": "command",
                        "command": "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh",
                        "timeout": 120,
                    }
                ],
            }
        ],
        "Stop": [{"hooks": [{"type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks/run.sh"}]}],
    }
}


def write_hooks(pdir: Path, hooks: dict) -> None:
    write(pdir / "hooks" / "hooks.json", json.dumps(hooks, ensure_ascii=False) + "\n")


def test_valid_hooks_json_passes(tmp_path):
    pdir = make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    write_hooks(pdir, VALID_HOOKS)
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 0, result.stderr


def test_unknown_key_in_hook_entry_fails(tmp_path):
    # dike-gate で実際に起きた回帰: hooks スキーマに無いキーは黙って無視される。
    pdir = make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    bad = json.loads(json.dumps(VALID_HOOKS))
    bad["hooks"]["PreToolUse"][0]["hooks"][0]["if"] = "Bash(git commit:*)"
    write_hooks(pdir, bad)
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "不明なキー 'if'" in result.stderr


def test_unknown_key_in_hook_group_fails(tmp_path):
    pdir = make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    bad = json.loads(json.dumps(VALID_HOOKS))
    bad["hooks"]["PreToolUse"][0]["condition"] = "always"
    write_hooks(pdir, bad)
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "不明なキー 'condition'" in result.stderr


def test_hook_entry_missing_command_fails(tmp_path):
    pdir = make_plugin(tmp_path, "muse-tech", skills=["muse-tech"])
    bad = json.loads(json.dumps(VALID_HOOKS))
    del bad["hooks"]["Stop"][0]["hooks"][0]["command"]
    write_hooks(pdir, bad)
    write_marketplace(tmp_path, ["muse-tech"])
    result = run_in(tmp_path)
    assert result.returncode == 1
    assert "'command' が無い" in result.stderr


def test_real_repo_hooks_json_is_valid():
    hooks_path = REPO_ROOT / "plugins" / "workflow" / "dike-gate" / "hooks" / "hooks.json"
    assert hooks_path.is_file()
    result = subprocess.run([sys.executable, str(SCRIPT)], text=True, capture_output=True)
    assert result.returncode == 0, result.stderr
