import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "validate-toolbox.py"


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


AGENT = """---
name: {name}
description: テスト用エージェント。
tools: Read, Grep
model: {model}
---

本文。
"""

SKILL = """---
name: {name}
description: テスト用スキル。
---

# {name}
"""


def make_script_copy(tmp_path):
    """Copy the validator so it resolves REPO_ROOT to the temp fixture root."""
    dest = tmp_path / "scripts" / "validate-toolbox.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    return dest


def run_in(tmp_path, *args):
    script = tmp_path / "scripts" / "validate-toolbox.py"
    if not script.exists():
        make_script_copy(tmp_path)
    return subprocess.run(
        [sys.executable, str(script), *args], text=True, capture_output=True
    )


def test_valid_toolbox_passes(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="opus"))
    write(tb / "agents" / "README.md", "# agents\n\n- `zeus`\n")
    write(tb / "skills" / "forge-implement" / "SKILL.md", SKILL.format(name="forge-implement"))
    write(tb / "skills" / "README.md", "# skills\n\n- `forge-implement`\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 0, result.stderr
    assert "OK: toolbox-greece" in result.stdout


def test_agent_missing_from_readme_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="opus"))
    write(tb / "agents" / "README.md", "# agents\n\nここに一覧。\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "一覧に記載されていない" in result.stderr


def test_skill_missing_from_readme_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "skills" / "forge-implement" / "SKILL.md", SKILL.format(name="forge-implement"))
    write(tb / "skills" / "README.md", "# skills\n\n空。\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "一覧に記載されていない" in result.stderr


def test_real_toolbox_greece_is_valid():
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "greece"], text=True, capture_output=True
    )
    assert result.returncode == 0, result.stderr


def test_missing_required_key_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", "---\nname: zeus\ndescription: x\ntools: Read\n---\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "model" in result.stderr


def test_name_mismatch_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="hermes", model="opus"))

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "一致しない" in result.stderr


def test_invalid_model_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="gpt-9"))

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "model" in result.stderr


def test_unknown_tool_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(
        tb / "agents" / "zeus.md",
        "---\nname: zeus\ndescription: x\ntools: Read, Reed, Bash\nmodel: opus\n---\n",
    )

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "不明なツール 'Reed'" in result.stderr


def test_mcp_and_wildcard_tools_pass(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(
        tb / "agents" / "zeus.md",
        "---\nname: zeus\ndescription: x\ntools: *, mcp__server__do\nmodel: opus\n---\n",
    )
    write(tb / "agents" / "README.md", "# agents\n\n- `zeus`\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 0, result.stderr


def test_duplicate_agent_name_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="opus"))
    write(tb / "agents" / "hermes.md", AGENT.format(name="zeus", model="opus"))

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "重複" in result.stderr


def test_skill_missing_manifest_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="opus"))
    (tb / "skills" / "broken").mkdir(parents=True)

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "SKILL.md が無い" in result.stderr


def _valid_base(tb):
    """設定検証テスト用の、agents/skills が妥当な最小 toolbox を作る。"""
    write(tb / "agents" / "zeus.md", AGENT.format(name="zeus", model="opus"))
    write(tb / "agents" / "README.md", "# agents\n\n- `zeus`\n")
    write(tb / "skills" / "forge-implement" / "SKILL.md", SKILL.format(name="forge-implement"))
    write(tb / "skills" / "README.md", "# skills\n\n- `forge-implement`\n")


def test_settings_invalid_json_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "settings.json", '{"permissions": {"deny": []},}\n')  # 末尾カンマ

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "JSON として不正" in result.stderr


def test_settings_absolute_path_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "settings.json", '{"permissions": {"deny": []}, "env": {"P": "/Users/me/bin"}}\n')

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "絶対パス" in result.stderr


def test_settings_missing_deny_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "settings.json", '{"permissions": {"allow": ["Read"]}}\n')

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "deny がない" in result.stderr


def test_mcp_invalid_json_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "mcp" / "servers.json", "{ not json }\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "JSON として不正" in result.stderr


def test_hooks_absolute_path_fails(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "hooks" / "run.sh", "#!/bin/sh\ncat /Users/me/secret\n")

    result = run_in(tmp_path, "greece")

    assert result.returncode == 1
    assert "絶対パス" in result.stderr


def test_valid_configs_pass(tmp_path):
    tb = tmp_path / "toolbox-greece"
    _valid_base(tb)
    write(tb / "settings.json", '{"permissions": {"allow": ["Read"], "deny": ["Bash(rm -rf:*)"]}}\n')
    write(tb / "mcp" / "servers.json", '{"mcpServers": {}}\n')
    write(tb / "hooks" / "run.sh", '#!/bin/sh\necho "$HOME/.claude"\n')

    result = run_in(tmp_path, "greece")

    assert result.returncode == 0, result.stderr
