#!/usr/bin/env python3
"""Validate agent and skill definitions inside one or more toolbox directories.

Checks the frontmatter of ``agents/*.md`` and ``skills/*/SKILL.md`` so that
definitions stay consistent as the toolbox grows: required keys are present,
``name`` matches the file/directory, names are unique, and ``model`` is known.

Usage::

    python3 scripts/validate-toolbox.py            # all toolbox* directories
    python3 scripts/validate-toolbox.py greece     # toolbox-greece only
    python3 scripts/validate-toolbox.py toolbox-greece
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

AGENT_REQUIRED_KEYS = ("name", "description", "tools", "model")
SKILL_REQUIRED_KEYS = ("name", "description")
ALLOWED_MODELS = {"opus", "sonnet", "haiku", "inherit"}


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
        if name:
            if name in seen:
                errors.append(f"{where}: name '{name}' が {seen[name].name} と重複")
            else:
                seen[name] = path


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


def validate_toolbox(toolbox: Path) -> list[str]:
    errors: list[str] = []
    rel = toolbox.name
    validate_agents(toolbox / "agents", rel, errors)
    validate_skills(toolbox / "skills", rel, errors)
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
