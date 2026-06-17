#!/usr/bin/env python3
"""Validate agent and skill definitions inside one or more toolbox directories.

Checks the frontmatter of ``agents/*.md`` and ``skills/*/SKILL.md`` so that
definitions stay consistent as the toolbox grows: required keys are present,
``name`` matches the file/directory, names are unique, and ``model`` is known.

Also checks distributed config files: ``settings.json`` (valid JSON, has a
``deny`` when ``permissions`` is present, no absolute paths), ``mcp/*.json``
(valid JSON, no absolute paths), and ``hooks/*`` scripts (no absolute paths).

Usage::

    python3 scripts/validate-toolbox.py            # all toolbox* directories
    python3 scripts/validate-toolbox.py greece     # toolbox-greece only
    python3 scripts/validate-toolbox.py toolbox-greece
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_REQUIRED_KEYS = ("name", "description", "tools", "model")
SKILL_REQUIRED_KEYS = ("name", "description")
# 配布される設定ファイルに混入してはいけない絶対パス / マシン固有パス。
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"/home/[A-Za-z0-9._-]+"),
    re.compile(r"[A-Za-z]:\\+Users", re.IGNORECASE),
)
ALLOWED_MODELS = {"opus", "sonnet", "haiku", "inherit"}
# agent の tools に書ける既知ツール。typo（例: Reed）を検出するために使う。
ALLOWED_TOOLS = {
    "Task", "Bash", "BashOutput", "KillShell", "Glob", "Grep", "Read",
    "Edit", "Write", "NotebookEdit", "WebFetch", "WebSearch", "TodoWrite",
    "SlashCommand",
}


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Return the leading ``key: value`` frontmatter block, or None if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        data[key.strip()] = value.strip()
    return None  # no closing fence


def is_valid_model(value: str) -> bool:
    return value in ALLOWED_MODELS or value.startswith("claude-")


def is_valid_tool(value: str) -> bool:
    # `*`（全許可）と MCP ツール（mcp__server__tool）は名前を固定できないため許容する。
    return value == "*" or value.startswith("mcp__") or value in ALLOWED_TOOLS


def check_readme_lists(readme: Path, names: list[str], rel: str, errors: list[str]) -> None:
    """各 name が README 内に記載されているか（一覧の更新漏れ）を確認する。"""
    if not names:
        return
    if not readme.is_file():
        errors.append(f"{rel}/{readme.name}: README が無いため一覧の整合を確認できない")
        return
    text = readme.read_text(encoding="utf-8")
    for name in names:
        if name not in text:
            errors.append(f"{rel}/{readme.name}: '{name}' が一覧に記載されていない")


def validate_agents(agents_dir: Path, rel: str, errors: list[str]) -> None:
    if not agents_dir.is_dir():
        return
    seen: dict[str, Path] = {}
    for path in sorted(agents_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        where = f"{rel}/agents/{path.name}"
        front = parse_frontmatter(path.read_text(encoding="utf-8"))
        if front is None:
            errors.append(f"{where}: frontmatter が見つからない")
            continue
        for key in AGENT_REQUIRED_KEYS:
            if not front.get(key):
                errors.append(f"{where}: 必須キー '{key}' が無い")
        name = front.get("name", "")
        if name and name != path.stem:
            errors.append(f"{where}: name '{name}' がファイル名 '{path.stem}' と一致しない")
        model = front.get("model", "")
        if model and not is_valid_model(model):
            errors.append(f"{where}: model '{model}' が不正")
        tools = front.get("tools", "")
        for tool in (t.strip() for t in tools.split(",")):
            if tool and not is_valid_tool(tool):
                errors.append(f"{where}: 不明なツール '{tool}'")
        if name:
            if name in seen:
                errors.append(f"{where}: name '{name}' が {seen[name].name} と重複")
            else:
                seen[name] = path
    check_readme_lists(agents_dir / "README.md", list(seen), f"{rel}/agents", errors)


def validate_skills(skills_dir: Path, rel: str, errors: list[str]) -> None:
    if not skills_dir.is_dir():
        return
    seen: dict[str, Path] = {}
    for skill_path in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        manifest = skill_path / "SKILL.md"
        where = f"{rel}/skills/{skill_path.name}/SKILL.md"
        if not manifest.is_file():
            errors.append(f"{where}: SKILL.md が無い")
            continue
        front = parse_frontmatter(manifest.read_text(encoding="utf-8"))
        if front is None:
            errors.append(f"{where}: frontmatter が見つからない")
            continue
        for key in SKILL_REQUIRED_KEYS:
            if not front.get(key):
                errors.append(f"{where}: 必須キー '{key}' が無い")
        name = front.get("name", "")
        if name and name != skill_path.name:
            errors.append(
                f"{where}: name '{name}' がディレクトリ名 '{skill_path.name}' と一致しない"
            )
        if name:
            if name in seen:
                errors.append(f"{where}: name '{name}' が重複")
            else:
                seen[name] = manifest
    check_readme_lists(skills_dir / "README.md", list(seen), f"{rel}/skills", errors)


def scan_absolute_paths(text: str, where: str, errors: list[str]) -> None:
    """配布物に絶対パス / マシン固有パスが混入していないか確認する。"""
    for pattern in ABSOLUTE_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(
                f"{where}: 絶対パス/マシン固有パスらしき記述 '{match.group(0)}'"
                "（'~' や '$HOME' を使う）"
            )
            return


def check_json(text: str, where: str, errors: list[str]) -> bool:
    """JSON として妥当か確認する。妥当なら True。"""
    try:
        json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{where}: JSON として不正（{exc.msg}, 行 {exc.lineno}）")
        return False
    return True


def validate_configs(toolbox: Path, rel: str, errors: list[str]) -> None:
    """配布される settings.json / hooks / mcp の妥当性と安全性を確認する。"""
    # settings.json: 妥当な JSON で、permissions があれば deny を持つ。絶対パス禁止。
    settings = toolbox / "settings.json"
    if settings.is_file():
        where = f"{rel}/settings.json"
        text = settings.read_text(encoding="utf-8")
        scan_absolute_paths(text, where, errors)
        if check_json(text, where, errors):
            data = json.loads(text)
            perms = data.get("permissions")
            if isinstance(perms, dict) and "deny" not in perms:
                errors.append(
                    f"{where}: permissions に deny がない"
                    "（破壊的操作を遮断する deny を明示する）"
                )

    # mcp/*.json: 妥当な JSON で絶対パス禁止。
    mcp_dir = toolbox / "mcp"
    if mcp_dir.is_dir():
        for path in sorted(mcp_dir.glob("*.json")):
            where = f"{rel}/mcp/{path.name}"
            text = path.read_text(encoding="utf-8")
            scan_absolute_paths(text, where, errors)
            check_json(text, where, errors)

    # hooks/*: スクリプトに絶対パスを書かない（$HOME 相対にする）。
    hooks_dir = toolbox / "hooks"
    if hooks_dir.is_dir():
        for path in sorted(hooks_dir.iterdir()):
            if not path.is_file() or path.name in ("README.md", ".gitkeep"):
                continue
            where = f"{rel}/hooks/{path.name}"
            scan_absolute_paths(path.read_text(encoding="utf-8"), where, errors)


def validate_toolbox(toolbox: Path) -> list[str]:
    errors: list[str] = []
    rel = toolbox.name
    validate_agents(toolbox / "agents", rel, errors)
    validate_skills(toolbox / "skills", rel, errors)
    validate_configs(toolbox, rel, errors)
    return errors


def resolve_toolboxes(args: list[str]) -> list[Path]:
    if args:
        paths = []
        for arg in args:
            name = arg if arg.startswith("toolbox") else f"toolbox-{arg}"
            paths.append(REPO_ROOT / name)
        return paths
    return sorted(p for p in REPO_ROOT.glob("toolbox*") if p.is_dir())


def main(argv: list[str]) -> int:
    toolboxes = resolve_toolboxes(argv)
    if not toolboxes:
        print("検証対象の toolbox が見つからない", file=sys.stderr)
        return 1
    all_errors: list[str] = []
    for toolbox in toolboxes:
        if not toolbox.is_dir():
            all_errors.append(f"{toolbox.name}: ディレクトリが存在しない")
            continue
        errors = validate_toolbox(toolbox)
        all_errors.extend(errors)
        if not errors:
            print(f"OK: {toolbox.name}")
    if all_errors:
        print("\n検証エラー:", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
