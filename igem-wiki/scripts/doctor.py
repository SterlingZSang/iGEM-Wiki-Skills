#!/usr/bin/env python3
"""Read-only health check for installed iGEM Wiki skills and checkpoints."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path


SKILLS = (
    "igem-wiki",
    "igem-wiki-story",
    "igem-wetlab-wiki",
    "igem-model-wiki",
    "igem-hp-wiki",
    "igem-implementation-wiki",
)
DOMAIN_SKILLS = SKILLS[1:]
LOCAL_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")
CHECKPOINT_HEADINGS = (
    "# Wiki work checkpoint",
    "## Context",
    "## Progress",
    "## Files and verification",
    "## Resume point",
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|api[_ -]?key|secret|private[_ -]?key)\b\s*[:=]\s*\S+"
)
IGNORED_NAMES = {".DS_Store"}
IGNORED_SUFFIXES = {".pyc"}
COLLECTION = "iGEM-Wiki-Skills"
MANIFEST_SCHEMA = 1
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect an iGEM Wiki skill installation without changing it."
    )
    parser.add_argument(
        "skill_root",
        type=Path,
        help="Directory containing installed igem-* skill folders, or the source repository root.",
    )
    parser.add_argument(
        "--source",
        type=Path,
        help="Optional source repository used for byte-for-byte staleness comparison.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Optional Wiki project root; checks .igem-wiki/checkpoint.md when present.",
    )
    parser.add_argument(
        "--as-of",
        type=dt.date.fromisoformat,
        default=dt.date.today(),
        help="Date used for season freshness checks (YYYY-MM-DD; defaults to today).",
    )
    parser.add_argument(
        "--max-season-age-days",
        type=int,
        default=60,
        help="Warn when the current-season snapshot is older than this many days.",
    )
    parser.add_argument("--json", action="store_true", help="Emit a JSON report.")
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Return success even when issues are found.",
    )
    return parser.parse_args()


def issue(
    issues: list[dict[str, object]],
    code: str,
    message: str,
    *,
    severity: str = "error",
    **details: object,
) -> None:
    item: dict[str, object] = {"severity": severity, "code": code, "message": message}
    item.update(details)
    issues.append(item)


def relative_label(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def contained(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_local_links(
    skill_dir: Path,
    skill_root: Path,
    issues: list[dict[str, object]],
) -> None:
    for markdown in sorted(skill_dir.rglob("*.md")):
        if markdown.is_symlink():
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target:
                continue
            if target.startswith("/"):
                issue(
                    issues,
                    "absolute-local-link",
                    f"{relative_label(markdown, skill_root)} contains an absolute local link",
                    path=relative_label(markdown, skill_root),
                )
                continue
            resolved = (markdown.parent / target).resolve()
            if not contained(resolved, skill_root.resolve()):
                issue(
                    issues,
                    "local-link-escapes-root",
                    f"{relative_label(markdown, skill_root)} links outside the skill root",
                    path=relative_label(markdown, skill_root),
                )
            elif not resolved.exists():
                issue(
                    issues,
                    "broken-local-link",
                    f"{relative_label(markdown, skill_root)} links to missing {raw_target}",
                    path=relative_label(markdown, skill_root),
                )


def included_file(path: Path) -> bool:
    return (
        not path.is_symlink()
        and path.is_file()
        and path.name not in IGNORED_NAMES
        and path.suffix not in IGNORED_SUFFIXES
        and "__pycache__" not in path.parts
    )


def validate_symlinks(
    skill_dir: Path,
    skill_root: Path,
    issues: list[dict[str, object]],
) -> None:
    for path in sorted(skill_dir.rglob("*")):
        if path.is_symlink():
            issue(
                issues,
                "symlink-not-portable",
                f"{relative_label(path, skill_root)} is a symbolic link",
                path=relative_label(path, skill_root),
            )


def file_inventory(skill_dir: Path) -> dict[str, str]:
    inventory: dict[str, str] = {}
    if not skill_dir.is_dir():
        return inventory
    for path in sorted(skill_dir.rglob("*")):
        if included_file(path):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            inventory[path.relative_to(skill_dir).as_posix()] = digest
    return inventory


def compare_source(
    skill: str,
    installed_root: Path,
    source_root: Path,
    issues: list[dict[str, object]],
) -> None:
    source_dir = source_root / skill
    if not source_dir.is_dir():
        issue(issues, "source-missing-skill", f"source does not contain {skill}", skill=skill)
        return
    installed = file_inventory(installed_root / skill)
    source = file_inventory(source_dir)
    for path in sorted(source.keys() - installed.keys()):
        issue(
            issues,
            "installed-file-missing",
            f"{skill}/{path} is missing from the installation",
            skill=skill,
            path=path,
        )
    for path in sorted(installed.keys() - source.keys()):
        issue(
            issues,
            "installed-file-extra",
            f"{skill}/{path} is not present in the selected source",
            skill=skill,
            path=path,
        )
    for path in sorted(installed.keys() & source.keys()):
        if installed[path] != source[path]:
            issue(
                issues,
                "installed-file-stale",
                f"{skill}/{path} differs from the selected source",
                skill=skill,
                path=path,
            )


def manifest_at(skill_dir: Path) -> dict[str, object] | None:
    path = skill_dir / "manifest.json"
    if not path.is_file() or path.is_symlink():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def version_at(root: Path | None, present: list[str] | None = None) -> str | None:
    if root is None:
        return None
    path = root / "VERSION"
    if path.is_file():
        value = path.read_text(encoding="utf-8").strip()
        return value or None
    versions = {
        str(manifest["version"])
        for skill in present or []
        if (manifest := manifest_at(root / skill)) is not None and manifest.get("version")
    }
    if len(versions) == 1:
        return versions.pop()
    return None


def inspect_season(
    skill_root: Path,
    coordinator_present: bool,
    as_of: dt.date,
    max_age_days: int,
) -> dict[str, object]:
    report: dict[str, object] = {
        "path": None,
        "verified_on": None,
        "age_days": None,
        "issues": [],
    }
    if not coordinator_present:
        return report
    if (skill_root / "igem-wiki").is_symlink():
        return report
    path = skill_root / "igem-wiki" / "references" / "seasons" / f"{as_of.year}-judging.md"
    report["path"] = str(path)
    season_issues: list[dict[str, object]] = []
    if not path.is_file():
        issue(
            season_issues,
            "current-season-snapshot-missing",
            f"no {as_of.year} judging snapshot is installed; verify current rules live",
            severity="warning",
        )
        report["issues"] = season_issues
        return report
    text = path.read_text(encoding="utf-8")
    match = re.search(r"Verified on (\d{4}-\d{2}-\d{2})", text)
    if not match:
        issue(
            season_issues,
            "season-verification-date-missing",
            "current-season judging snapshot has no verification date",
            severity="warning",
        )
    else:
        try:
            verified_on = dt.date.fromisoformat(match.group(1))
        except ValueError:
            issue(
                season_issues,
                "season-verification-date-invalid",
                "current-season judging snapshot has an invalid verification date",
                severity="warning",
            )
        else:
            age_days = (as_of - verified_on).days
            report["verified_on"] = verified_on.isoformat()
            report["age_days"] = age_days
            if age_days < 0:
                issue(
                    season_issues,
                    "season-verification-date-future",
                    "current-season judging snapshot is dated in the future",
                    severity="warning",
                )
            elif age_days > max_age_days:
                issue(
                    season_issues,
                    "season-snapshot-stale",
                    f"current-season judging snapshot is {age_days} days old; verify unstable rules live",
                    severity="warning",
                )
    report["issues"] = season_issues
    return report


def inspect_checkpoint(project_root: Path | None) -> dict[str, object]:
    report: dict[str, object] = {"path": None, "present": False, "issues": []}
    if project_root is None:
        return report
    path = project_root.resolve() / ".igem-wiki" / "checkpoint.md"
    report["path"] = str(path)
    if (
        path.is_symlink()
        or path.parent.is_symlink()
        or not contained(path.resolve(), project_root.resolve())
    ):
        checkpoint_issues: list[dict[str, object]] = []
        issue(
            checkpoint_issues,
            "checkpoint-symlink-not-allowed",
            "checkpoint path uses a symbolic link; content was not read",
        )
        report["issues"] = checkpoint_issues
        return report
    if not path.is_file():
        return report
    report["present"] = True
    checkpoint_issues: list[dict[str, object]] = []
    text = path.read_text(encoding="utf-8")
    for heading in CHECKPOINT_HEADINGS:
        if heading not in text:
            issue(
                checkpoint_issues,
                "checkpoint-heading-missing",
                f"checkpoint lacks required heading: {heading}",
            )
    for line_number, line in enumerate(text.splitlines(), start=1):
        if SECRET_ASSIGNMENT.search(line):
            issue(
                checkpoint_issues,
                "checkpoint-possible-secret",
                f"checkpoint may contain a credential on line {line_number}; content was not displayed",
                line=line_number,
            )
    report["issues"] = checkpoint_issues
    return report


def build_report(args: argparse.Namespace) -> dict[str, object]:
    requested_root = args.skill_root.expanduser().absolute()
    root_is_symlink = requested_root.is_symlink()
    requested_skill = (
        requested_root.name
        if not root_is_symlink
        and requested_root.name in SKILLS
        and (requested_root / "SKILL.md").is_file()
        else None
    )
    skill_root = (
        requested_root.parent
        if requested_skill
        else requested_root
    )
    source_root = args.source.resolve() if args.source else None
    discovered = (
        []
        if root_is_symlink
        else [skill for skill in SKILLS if (skill_root / skill).is_dir()]
    )
    present = (
        [requested_skill]
        if requested_skill and requested_skill != "igem-wiki"
        else discovered
    )
    coordinator_present = "igem-wiki" in present
    expected = list(SKILLS if coordinator_present else DOMAIN_SKILLS)
    missing = [skill for skill in expected if skill not in present]
    issues: list[dict[str, object]] = []

    if root_is_symlink:
        issue(
            issues,
            "skill-root-symlink-not-allowed",
            "skill root is a symbolic link and was not inspected",
        )

    if args.max_season_age_days < 1:
        issue(
            issues,
            "invalid-season-age",
            "--max-season-age-days must be positive",
        )

    if not present:
        issue(
            issues,
            "no-skills-found",
            f"no recognized igem-* skill folders found under {skill_root}",
        )
    elif coordinator_present:
        for skill in missing:
            issue(
                issues,
                "coordinator-sibling-missing",
                f"igem-wiki requires sibling skill {skill}",
                skill=skill,
            )

    for skill in present:
        skill_dir = skill_root / skill
        if skill_dir.is_symlink():
            issue(
                issues,
                "skill-directory-symlink-not-allowed",
                f"{skill} is a symbolic-link directory and was not inspected",
                skill=skill,
            )
            continue
        for required in (
            skill_dir / "SKILL.md",
            skill_dir / "agents" / "openai.yaml",
            skill_dir / "manifest.json",
        ):
            if not required.is_file():
                issue(
                    issues,
                    "required-file-missing",
                    f"{relative_label(required, skill_root)} is missing",
                    skill=skill,
                    path=relative_label(required, skill_root),
                )
        manifest = manifest_at(skill_dir)
        if (skill_dir / "manifest.json").is_file() and manifest is None:
            issue(
                issues,
                "manifest-invalid",
                f"{skill}/manifest.json is invalid",
                skill=skill,
            )
        elif manifest is not None:
            if manifest.get("schema_version") != MANIFEST_SCHEMA:
                issue(
                    issues,
                    "manifest-schema-unsupported",
                    f"{skill}/manifest.json has an unsupported schema",
                    skill=skill,
                )
            if manifest.get("collection") != COLLECTION:
                issue(
                    issues,
                    "manifest-collection-mismatch",
                    f"{skill}/manifest.json names a different collection",
                    skill=skill,
                )
            if manifest.get("skill") != skill:
                issue(
                    issues,
                    "manifest-skill-mismatch",
                    f"{skill}/manifest.json names a different skill",
                    skill=skill,
                )
            if not manifest.get("version"):
                issue(
                    issues,
                    "manifest-version-missing",
                    f"{skill}/manifest.json has no version",
                    skill=skill,
                )
            elif not SEMVER.fullmatch(str(manifest["version"])):
                issue(
                    issues,
                    "manifest-version-invalid",
                    f"{skill}/manifest.json has an invalid semantic version",
                    skill=skill,
                )
        validate_symlinks(skill_dir, skill_root, issues)
        validate_local_links(skill_dir, skill_root, issues)
        if source_root is not None:
            compare_source(skill, skill_root, source_root, issues)

    manifest_versions = {
        str(manifest["version"])
        for skill in present
        if not (skill_root / skill).is_symlink()
        and (manifest := manifest_at(skill_root / skill)) is not None
        and manifest.get("version")
    }
    if len(manifest_versions) > 1:
        issue(
            issues,
            "installed-version-mismatch",
            "installed skill manifests do not agree on one version",
        )

    checkpoint = inspect_checkpoint(args.project_root)
    issues.extend(checkpoint["issues"])
    season = inspect_season(
        skill_root,
        coordinator_present,
        args.as_of,
        args.max_season_age_days,
    )
    issues.extend(season["issues"])
    mode = "full-collection" if coordinator_present else "standalone-domain"
    return {
        "requested_root": str(requested_root),
        "selected_skill": requested_skill,
        "root": str(skill_root),
        "expected_mode": mode,
        "present_skills": present,
        "missing_skills": missing if coordinator_present else [],
        "installed_version": (
            None if root_is_symlink else version_at(skill_root, present)
        ),
        "source_version": version_at(source_root),
        "source": str(source_root) if source_root else None,
        "issues": issues,
        "checkpoint": checkpoint,
        "season": season,
    }


def render_text(report: dict[str, object]) -> str:
    present = report["present_skills"]
    issues = report["issues"]
    lines = [
        "iGEM Wiki skill doctor (read-only)",
        f"Root: {report['root']}",
        f"Mode: {report['expected_mode']}",
        f"Skills found: {', '.join(present) if present else 'none'}",
    ]
    if report["installed_version"]:
        lines.append(f"Installed version: {report['installed_version']}")
    if report["source_version"]:
        lines.append(f"Declared source version: {report['source_version']}")
    checkpoint = report["checkpoint"]
    if checkpoint["path"]:
        state = "present" if checkpoint["present"] else "not present (optional)"
        lines.append(f"Checkpoint: {checkpoint['path']} [{state}]")
    errors = [item for item in issues if item["severity"] == "error"]
    warnings = [item for item in issues if item["severity"] == "warning"]
    if issues:
        lines.append(f"Errors: {len(errors)}; warnings: {len(warnings)}")
        lines.extend(
            f"- [{item['severity']}:{item['code']}] {item['message']}" for item in issues
        )
    else:
        lines.append("Status: healthy")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = build_report(args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
    has_errors = any(item["severity"] == "error" for item in report["issues"])
    return 0 if args.no_fail or not has_errors else 1


if __name__ == "__main__":
    sys.exit(main())
