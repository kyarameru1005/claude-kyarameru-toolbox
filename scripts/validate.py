#!/usr/bin/env python3
"""Validate the plugin marketplace and every plugin under ``plugins/``.

Checks performed:

* ``.claude-plugin/marketplace.json``: valid JSON, required keys, kebab-case and
  unique plugin names, every ``source`` resolves to a plugin directory, and the
  entry name matches that plugin's ``plugin.json`` name. No absolute paths.
* each ``plugins/<name>/``: ``.claude-plugin/plugin.json`` is valid JSON, ``name``
  matches the directory and is kebab-case, every ``dependencies`` entry refers to a
  plugin that exists, and no absolute paths leak in. ``skills/*/SKILL.md`` and
  ``agents/*.md`` frontmatter are checked for required keys and consistency.
* marketplace listing and ``plugins/`` directory are kept in sync (no orphans).

Usage::

    python3 scripts/validate.py            # validate everything
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE = REPO_ROOT / ".claude-plugin" / "marketplace.json"
PLUGINS_DIR = REPO_ROOT / "plugins"

AGENT_REQUIRED_KEYS = ("name", "description", "tools", "model")
SKILL_REQUIRED_KEYS = ("description",)
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ABSOLUTE_PATH_PATTERNS = (
    re.compile(r"/Users/"),
    re.compile(r"/home/[A-Za-z0-9._-]+"),
    re.compile(r"[A-Za-z]:\\+Users", re.IGNORECASE),
)
ALLOWED_MODELS = {"opus", "sonnet", "haiku", "inherit"}
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
    return value == "*" or value.startswith("mcp__") or value in ALLOWED_TOOLS


def scan_absolute_paths(text: str, where: str, errors: list[str]) -> None:
    for pattern in ABSOLUTE_PATH_PATTERNS:
        match = pattern.search(text)
        if match:
            errors.append(
                f"{where}: 絶対パス/マシン固有パスらしき記述 '{match.group(0)}'"
                "（'~' や '$HOME' を使う）"
            )
            return


def load_json(path: Path, where: str, errors: list[str]):
    text = path.read_text(encoding="utf-8")
    scan_absolute_paths(text, where, errors)
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"{where}: JSON として不正（{exc.msg}, 行 {exc.lineno}）")
        return None


def validate_agents(agents_dir: Path, rel: str, errors: list[str]) -> None:
    if not agents_dir.is_dir():
        return
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
        for tool in (t.strip() for t in front.get("tools", "").split(",")):
            if tool and not is_valid_tool(tool):
                errors.append(f"{where}: 不明なツール '{tool}'")


def validate_skills(skills_dir: Path, rel: str, errors: list[str]) -> None:
    if not skills_dir.is_dir():
        return
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


def validate_plugin(
    pdir: Path, all_names: set[str], errors: list[str], versions: dict[str, str]
) -> str | None:
    """Validate one plugin directory. Returns the declared plugin name (or None).

    Records the plugin's declared ``version`` in ``versions`` (keyed by rel path)
    so the caller can check that every plugin shares one version.
    """
    rel = str(pdir.relative_to(REPO_ROOT))
    manifest_path = pdir / ".claude-plugin" / "plugin.json"
    if not manifest_path.is_file():
        errors.append(f"{rel}: .claude-plugin/plugin.json が無い")
        return None
    data = load_json(manifest_path, f"{rel}/.claude-plugin/plugin.json", errors)
    if data is None:
        return None

    versions[rel] = data.get("version", "")
    name = data.get("name", "")
    if not name:
        errors.append(f"{rel}: plugin.json に 'name' が無い")
    else:
        if name != pdir.name:
            errors.append(f"{rel}: name '{name}' がディレクトリ名 '{pdir.name}' と一致しない")
        if not KEBAB_RE.match(name):
            errors.append(f"{rel}: name '{name}' が kebab-case でない")

    for dep in data.get("dependencies", []) or []:
        dep_name = dep if isinstance(dep, str) else dep.get("name", "")
        # marketplace 外（別 marketplace）依存は対象外。
        if isinstance(dep, dict) and dep.get("marketplace"):
            continue
        if dep_name and dep_name not in all_names:
            errors.append(f"{rel}: dependencies の '{dep_name}' が存在しない")

    validate_agents(pdir / "agents", rel, errors)
    validate_skills(pdir / "skills", rel, errors)
    return name or None


def validate_versions(data: dict, plugin_versions: dict[str, str], errors: list[str]) -> None:
    """全 plugin と marketplace.metadata.version が単一 version に揃っているか検査する。

    このリポジトリは全 plugin を同一 version で一括運用する（kairos-release スキル）。
    version が割れると「更新が届かない」事故につながるため機械的に守る。
    """
    where = ".claude-plugin/marketplace.json"
    distinct = sorted({v for v in plugin_versions.values() if v})
    missing = sorted(rel for rel, v in plugin_versions.items() if not v)
    for rel in missing:
        errors.append(f"{rel}/.claude-plugin/plugin.json: 'version' が無い")
    if len(distinct) > 1:
        errors.append(
            f"plugin の version が揃っていない（{', '.join(distinct)}）"
            "。全 plugin を同一 version にする"
        )
    common = distinct[0] if len(distinct) == 1 else None
    meta_version = (data.get("metadata") or {}).get("version")
    if common and meta_version and meta_version != common:
        errors.append(
            f"{where}: metadata.version '{meta_version}' が plugin の version '{common}' と一致しない"
        )


def validate_marketplace(
    plugin_names: set[str], plugin_versions: dict[str, str], errors: list[str]
) -> None:
    where = ".claude-plugin/marketplace.json"
    if not MARKETPLACE.is_file():
        errors.append(f"{where}: が存在しない")
        return
    data = load_json(MARKETPLACE, where, errors)
    if data is None:
        return
    validate_versions(data, plugin_versions, errors)
    for key in ("name", "owner", "plugins"):
        if key not in data:
            errors.append(f"{where}: 必須キー '{key}' が無い")
    if data.get("name") and not KEBAB_RE.match(data["name"]):
        errors.append(f"{where}: marketplace name '{data['name']}' が kebab-case でない")
    owner = data.get("owner")
    if owner is not None and not (isinstance(owner, dict) and owner.get("name")):
        errors.append(f"{where}: owner.name が無い")

    plugin_root = (data.get("metadata") or {}).get("pluginRoot", "").lstrip("./")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        errors.append(f"{where}: plugins が空、またはリストでない")
        return

    listed: set[str] = set()
    for index, entry in enumerate(plugins):
        loc = f"{where}: plugins[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{loc}: オブジェクトでない")
            continue
        pname = entry.get("name", "")
        if not pname:
            errors.append(f"{loc}: 'name' が無い")
            continue
        loc = f"{where}: plugin '{pname}'"
        if not KEBAB_RE.match(pname):
            errors.append(f"{loc}: name が kebab-case でない")
        if "version" in entry:
            errors.append(
                f"{loc}: marketplace entry に version を書かない"
                "（plugin.json を真実にする）"
            )
        if pname in listed:
            errors.append(f"{loc}: name が重複")
        listed.add(pname)
        source = entry.get("source")
        if not source:
            errors.append(f"{loc}: 'source' が無い")
            continue
        if not isinstance(source, str):
            continue  # github/url など外部 source は対象外
        if ".." in Path(source).parts:
            errors.append(f"{loc}: source '{source}' に '..' を使えない")
            continue
        rel_source = source.lstrip("./")
        target = REPO_ROOT / plugin_root / rel_source if plugin_root else REPO_ROOT / rel_source
        if not target.is_dir():
            errors.append(f"{loc}: source '{source}' のディレクトリが無い")
        elif target.name != pname:
            errors.append(f"{loc}: source ディレクトリ名 '{target.name}' が name と一致しない")

    # plugins/ ディレクトリと marketplace 一覧の同期を確認する。
    for missing in sorted(plugin_names - listed):
        errors.append(f"{where}: plugins/{missing} が marketplace に未掲載")
    for extra in sorted(listed - plugin_names):
        errors.append(f"{where}: '{extra}' に対応する plugins/ ディレクトリが無い")


def main() -> int:
    errors: list[str] = []
    if not PLUGINS_DIR.is_dir():
        print("plugins/ が見つからない", file=sys.stderr)
        return 1
    # plugin はカテゴリ配下にネストしうるので manifest を起点に集める。
    plugin_dirs = sorted(
        {mf.parent.parent for mf in PLUGINS_DIR.glob("**/.claude-plugin/plugin.json")}
    )
    plugin_names = {p.name for p in plugin_dirs}

    versions: dict[str, str] = {}
    for pdir in plugin_dirs:
        validate_plugin(pdir, plugin_names, errors, versions)
    validate_marketplace(plugin_names, versions, errors)

    if errors:
        print("検証エラー:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1
    print(f"OK: marketplace + {len(plugin_dirs)} plugins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
