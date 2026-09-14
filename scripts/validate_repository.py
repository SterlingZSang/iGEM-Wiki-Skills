#!/usr/bin/env python3
"""Validate the portable iGEM wiki skill collection without third-party packages."""

from __future__ import annotations

import re
import shutil
import subprocess
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
LOCAL_LINK = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)]+)\)")
FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
ACTION_USE = re.compile(r"^\s*-\s+uses:\s+([^@\s]+)@([^\s#]+)", re.MULTILINE)
INPUT_PREFLIGHT_HEADING = "## Run the input preflight"
DELIVERY_CONTRACT_HEADING = "## Confirm the delivery contract"
RESUME_HEADING = "## Resume interrupted work"
CLOSE_LOOP_HEADING = "## Close the work loop"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def validate_skill(skill_name: str, failures: list[str]) -> None:
    skill_dir = ROOT / skill_name
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        fail(f"{skill_name}: missing SKILL.md", failures)
        return

    text = skill_file.read_text(encoding="utf-8")
    match = FRONTMATTER.match(text)
    if not match:
        fail(f"{skill_name}: invalid YAML frontmatter boundary", failures)
        return

    frontmatter = match.group(1)
    name_match = re.search(r"^name:\s*[\"']?([^\"'\n]+)", frontmatter, re.MULTILINE)
    description_match = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not name_match or name_match.group(1).strip() != skill_name:
        fail(f"{skill_name}: frontmatter name must match directory", failures)
    if not description_match or not description_match.group(1).strip():
        fail(f"{skill_name}: missing description", failures)
    if INPUT_PREFLIGHT_HEADING not in text:
        fail(f"{skill_name}: missing the shared input-preflight contract", failures)
    if DELIVERY_CONTRACT_HEADING not in text:
        fail(f"{skill_name}: missing the shared delivery contract", failures)
    if RESUME_HEADING not in text:
        fail(f"{skill_name}: missing the shared resume contract", failures)
    if CLOSE_LOOP_HEADING not in text:
        fail(f"{skill_name}: missing the shared work-loop closure", failures)

    ui_file = skill_dir / "agents" / "openai.yaml"
    if not ui_file.is_file():
        fail(f"{skill_name}: missing agents/openai.yaml", failures)
    else:
        ui = ui_file.read_text(encoding="utf-8")
        for field in ("display_name:", "short_description:", "default_prompt:"):
            if field not in ui:
                fail(f"{skill_name}: openai.yaml missing {field}", failures)
        if f"${skill_name}" not in ui:
            fail(f"{skill_name}: default prompt must mention ${skill_name}", failures)


def validate_links(failures: list[str]) -> None:
    for markdown in ROOT.rglob("*.md"):
        if ".git" in markdown.parts:
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in LOCAL_LINK.findall(text):
            target = raw_target.split("#", 1)[0].strip()
            if not target or target.startswith("/"):
                continue
            resolved = (markdown.parent / target).resolve()
            if not resolved.exists():
                fail(f"{markdown.relative_to(ROOT)}: broken local link {raw_target}", failures)


def validate_installed_layout(failures: list[str]) -> None:
    """Confirm links still resolve when only the six installable skill folders are copied."""
    with tempfile.TemporaryDirectory() as temporary:
        skill_root = Path(temporary) / ".agents" / "skills"
        skill_root.mkdir(parents=True)
        for skill in SKILLS:
            shutil.copytree(ROOT / skill, skill_root / skill)
        for markdown in skill_root.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            for raw_target in LOCAL_LINK.findall(text):
                target = raw_target.split("#", 1)[0].strip()
                if not target or target.startswith("/"):
                    continue
                if not (markdown.parent / target).resolve().exists():
                    fail(
                        f"installed layout {markdown.relative_to(skill_root)}: broken local link {raw_target}",
                        failures,
                    )


def validate_release_resources(failures: list[str]) -> None:
    required = (
        "igem-wiki/references/ai-integrity.md",
        "igem-wiki/references/claim-evidence-register.md",
        "igem-wiki/references/cross-domain-awards.md",
        "igem-wiki/references/sampling-policy.md",
        "igem-wiki/references/seasons/2026-judging.md",
        "igem-wiki/assets/templates/whole-wiki-evidence-map.md",
        "igem-wiki/assets/templates/page-brief.md",
        "igem-wiki/assets/templates/figure-evidence-card.md",
        "igem-wiki/assets/templates/team-intake.md",
        "igem-wiki/assets/templates/judging-readiness-matrix.md",
        "igem-wiki/assets/templates/wiki-production-board.md",
        "igem-wiki/assets/templates/browser-qa-report.md",
        "igem-wiki/assets/templates/resume-checkpoint.md",
        "igem-wiki/scripts/audit_claim_consistency.py",
        "igem-wiki/scripts/audit_static_wiki.py",
        "igem-wetlab-wiki/assets/templates/dbtl-cycle.md",
        "igem-model-wiki/assets/templates/model-card.md",
        "igem-model-wiki/references/generated/model-taxonomy.md",
        "igem-model-wiki/references/generated/model-modules.md",
        "igem-hp-wiki/assets/templates/integration-log.md",
        "igem-implementation-wiki/assets/templates/readiness-matrix.md",
        "corpus/schema.md",
        "corpus/award_records.csv",
        "corpus/page_reviews.csv",
        "corpus/model_review_metadata.csv",
        "corpus/model_modules.csv",
        "corpus/source_manifest.csv",
        "corpus/snapshots/igem-competitions.json",
        "scripts/build_corpus.py",
        "scripts/import_annual_results.py",
        "scripts/query_corpus.py",
        "scripts/validate_evals.py",
        "scripts/validate_version.py",
        "tests/test_tools.py",
        "evals/README.md",
        "RELEASING.md",
    )
    for relative in required:
        if not (ROOT / relative).is_file():
            fail(f"missing release resource: {relative}", failures)

    season = ROOT / "igem-wiki/references/seasons/2026-judging.md"
    if season.is_file():
        text = season.read_text(encoding="utf-8")
        if "Verified on " not in text:
            fail("2026 judging snapshot lacks a verification date", failures)
        if "competition.igem.org" not in text:
            fail("2026 judging snapshot lacks official sources", failures)


def validate_corpus(failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_corpus.py"), "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        detail = (result.stdout + result.stderr).strip()
        fail(f"corpus validation failed: {detail}", failures)


def validate_auxiliary_checks(failures: list[str]) -> None:
    for script, label in (
        ("validate_version.py", "version metadata"),
        ("validate_evals.py", "evaluation contracts"),
    ):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / script)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            detail = (result.stdout + result.stderr).strip()
            fail(f"{label} validation failed: {detail}", failures)


def validate_placeholders(failures: list[str]) -> None:
    marker = re.compile(r"\[TODO:|\bPLACEHOLDER\b|\bTBD\b")
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".yaml", ".yml", ".cff"}:
            continue
        if marker.search(path.read_text(encoding="utf-8")):
            fail(f"{path.relative_to(ROOT)}: unfinished placeholder", failures)


def validate_action_pins(failures: list[str]) -> None:
    workflow_root = ROOT / ".github" / "workflows"
    for path in workflow_root.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8")
        for action, reference in ACTION_USE.findall(text):
            if action.startswith("./"):
                continue
            if not re.fullmatch(r"[0-9a-f]{40}", reference):
                fail(
                    f"{path.relative_to(ROOT)}: action {action} is not pinned to a full commit hash",
                    failures,
                )


def main() -> int:
    failures: list[str] = []
    for skill in SKILLS:
        validate_skill(skill, failures)
    validate_links(failures)
    validate_installed_layout(failures)
    validate_release_resources(failures)
    validate_corpus(failures)
    validate_auxiliary_checks(failures)
    validate_placeholders(failures)
    validate_action_pins(failures)

    if failures:
        print("Repository validation failed:")
        for item in failures:
            print(f"- {item}")
        return 1

    template_count = len(list(ROOT.glob("igem-*/assets/templates/*.md")))
    print(f"Validated {len(SKILLS)} skills and {template_count} templates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
