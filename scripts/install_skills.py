#!/usr/bin/env python3
"""Preview or apply a local iGEM Wiki skill installation with backups."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "igem-wiki",
    "igem-wiki-story",
    "igem-wetlab-wiki",
    "igem-model-wiki",
    "igem-hp-wiki",
    "igem-implementation-wiki",
)
IGNORED_NAMES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}
COLLECTION = "iGEM-Wiki-Skills"
MANIFEST_SCHEMA = 1
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or install iGEM Wiki skills from this trusted checkout."
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Destination skills directory, such as PROJECT/.agents/skills.",
    )
    parser.add_argument(
        "--skill",
        action="append",
        choices=SKILLS,
        help="Install one named skill; repeat for more. Omit to select all six.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the displayed plan. Without this flag the command is read-only.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a JSON report.")
    return parser.parse_args()


def include_file(path: Path) -> bool:
    return (
        path.is_file()
        and not path.is_symlink()
        and path.name not in IGNORED_NAMES
        and path.suffix not in IGNORED_SUFFIXES
        and "__pycache__" not in path.parts
    )


def inventory(directory: Path) -> dict[str, str]:
    if not directory.is_dir():
        return {}
    files: dict[str, str] = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"symbolic links are not supported: {path}")
        if include_file(path):
            files[path.relative_to(directory).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return files


def read_manifest(skill_dir: Path) -> dict[str, object]:
    path = skill_dir / "manifest.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"invalid manifest: {path}") from error
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be an object: {path}")
    return data


def validate_source(selected: list[str]) -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        raise ValueError("source VERSION is not valid semantic versioning")
    for skill in selected:
        skill_dir = ROOT / skill
        if skill_dir.is_symlink():
            raise ValueError(f"source skill must not be a symbolic link: {skill}")
        if not (skill_dir / "SKILL.md").is_file():
            raise ValueError(f"source skill is incomplete: {skill}")
        if not (skill_dir / "agents" / "openai.yaml").is_file():
            raise ValueError(f"source UI metadata is missing: {skill}")
        manifest = read_manifest(skill_dir)
        if (
            manifest.get("schema_version") != MANIFEST_SCHEMA
            or manifest.get("collection") != COLLECTION
            or manifest.get("skill") != skill
            or manifest.get("version") != version
        ):
            raise ValueError(f"source manifest does not match {skill} at v{version}")
        inventory(skill_dir)
    return version


def validate_target(target: Path) -> Path:
    if target.is_symlink():
        raise ValueError("target skills directory must not be a symbolic link")
    resolved = target.resolve()
    if resolved in {Path("/"), Path.home().resolve()}:
        raise ValueError("refusing to use a broad filesystem or home-directory target")
    if resolved.exists() and not resolved.is_dir():
        raise ValueError("target exists but is not a directory")
    return resolved


def plan_install(target: Path, selected: list[str], version: str) -> dict[str, object]:
    changes: list[dict[str, object]] = []
    for skill in selected:
        source_files = inventory(ROOT / skill)
        target_dir = target / skill
        target_files = inventory(target_dir)
        missing = sorted(source_files.keys() - target_files.keys())
        extra = sorted(target_files.keys() - source_files.keys())
        changed = sorted(
            path
            for path in source_files.keys() & target_files.keys()
            if source_files[path] != target_files[path]
        )
        if not target_dir.exists():
            action = "install"
        elif missing or extra or changed:
            action = "update"
        else:
            action = "unchanged"
        changes.append(
            {
                "skill": skill,
                "action": action,
                "missing_files": len(missing),
                "extra_files": len(extra),
                "changed_files": len(changed),
            }
        )
    return {
        "source": str(ROOT),
        "target": str(target),
        "version": version,
        "mode": "preview",
        "selected_skills": selected,
        "changes": changes,
        "applied": False,
        "backup": None,
    }


def apply_plan(report: dict[str, object]) -> None:
    target = Path(str(report["target"]))
    changed = [item for item in report["changes"] if item["action"] != "unchanged"]
    if not changed:
        report["mode"] = "apply"
        report["applied"] = True
        return

    target.mkdir(parents=True, exist_ok=True)
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_container = target / ".igem-wiki-backups"
    if backup_container.is_symlink():
        raise ValueError(
            f"refusing to use symbolic-link backup directory: {backup_container}"
        )
    backup_root = backup_container / timestamp
    existing = [
        target / str(item["skill"])
        for item in changed
        if (target / str(item["skill"])).exists()
    ]

    with tempfile.TemporaryDirectory(prefix=".igem-wiki-stage-", dir=target) as temporary:
        stage = Path(temporary)
        new_root = stage / "new"
        old_root = stage / "old"
        new_root.mkdir()
        old_root.mkdir()
        for item in changed:
            skill = str(item["skill"])
            shutil.copytree(ROOT / skill, new_root / skill)
            inventory(new_root / skill)

        if existing:
            backup_root.mkdir(parents=True)
            for current in existing:
                if current.is_symlink():
                    raise ValueError(f"refusing to replace symbolic link: {current}")
                shutil.copytree(current, backup_root / current.name)

        installed: list[str] = []
        try:
            for item in changed:
                skill = str(item["skill"])
                current = target / skill
                moved_previous = False
                if current.exists():
                    os.replace(current, old_root / skill)
                    moved_previous = True
                try:
                    os.replace(new_root / skill, current)
                except Exception:
                    if moved_previous:
                        os.replace(old_root / skill, current)
                    raise
                installed.append(skill)
            for skill in installed:
                if inventory(target / skill) != inventory(ROOT / skill):
                    raise RuntimeError(f"post-install verification failed for {skill}")
        except Exception:
            for skill in reversed(installed):
                current = target / skill
                if current.exists():
                    shutil.rmtree(current)
                previous = old_root / skill
                if previous.exists():
                    os.replace(previous, current)
            raise

    report["mode"] = "apply"
    report["applied"] = True
    report["backup"] = str(backup_root) if existing else None


def render_text(report: dict[str, object]) -> str:
    lines = [
        f"iGEM Wiki Skills v{report['version']} installation {report['mode']}",
        f"Source: {report['source']}",
        f"Target: {report['target']}",
    ]
    for item in report["changes"]:
        lines.append(
            f"- {item['skill']}: {item['action']} "
            f"(missing {item['missing_files']}, changed {item['changed_files']}, "
            f"extra {item['extra_files']})"
        )
    if report["mode"] == "preview":
        lines.append("No files changed. Re-run with --apply to execute this exact selection.")
    elif report["backup"]:
        lines.append(f"Backup: {report['backup']}")
    else:
        lines.append("Applied successfully; no previous skill directories required backup.")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    selected = list(dict.fromkeys(args.skill or SKILLS))
    try:
        target = validate_target(args.target)
        version = validate_source(selected)
        report = plan_install(target, selected, version)
        if args.apply:
            apply_plan(report)
    except (OSError, RuntimeError, ValueError) as error:
        if args.json:
            print(json.dumps({"error": str(error)}, ensure_ascii=False, indent=2))
        else:
            print(f"Installation aborted: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
