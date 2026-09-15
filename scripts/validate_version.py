#!/usr/bin/env python3
"""Validate release-version metadata without third-party dependencies."""

from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SKILLS = (
    "igem-wiki",
    "igem-wiki-story",
    "igem-wetlab-wiki",
    "igem-model-wiki",
    "igem-hp-wiki",
    "igem-implementation-wiki",
)
REPOSITORY = "https://github.com/SterlingZSang/iGEM-Wiki-Skills"


def main() -> int:
    failures: list[str] = []
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        failures.append(f"VERSION is not a stable semantic version: {version!r}")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    citation_version = re.search(r"^version:\s*([^\s]+)\s*$", citation, re.MULTILINE)
    citation_date = re.search(r"^date-released:\s*(\d{4}-\d{2}-\d{2})\s*$", citation, re.MULTILINE)
    if not citation_version or citation_version.group(1) != version:
        failures.append("CITATION.cff version does not match VERSION")
    if not citation_date:
        failures.append("CITATION.cff lacks an ISO date-released")
    else:
        try:
            dt.date.fromisoformat(citation_date.group(1))
        except ValueError:
            failures.append("CITATION.cff date-released is invalid")
    for field in ("repository-code", "url"):
        if f'{field}: "{REPOSITORY}"' not in citation:
            failures.append(f"CITATION.cff {field} does not use the canonical repository")

    for skill in SKILLS:
        manifest_path = ROOT / skill / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            failures.append(f"{skill}: missing or invalid manifest.json")
            continue
        if manifest.get("schema_version") != 1:
            failures.append(f"{skill}: unsupported manifest schema")
        if manifest.get("collection") != "iGEM-Wiki-Skills":
            failures.append(f"{skill}: manifest collection mismatch")
        if manifest.get("skill") != skill:
            failures.append(f"{skill}: manifest skill mismatch")
        if manifest.get("version") != version:
            failures.append(f"{skill}: manifest version does not match VERSION")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"Current release: **v{version}**" not in readme:
        failures.append("README current release does not match VERSION")
    if "working tree also contains unreleased" in readme.casefold():
        failures.append("README must not describe committed main-branch content as working-tree content")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    release = re.search(
        rf"^## \[{re.escape(version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})$",
        changelog,
        re.MULTILINE,
    )
    if not release:
        failures.append(f"CHANGELOG lacks a dated [{version}] release section")
    elif citation_date and release.group(1) != citation_date.group(1):
        failures.append("CHANGELOG release date does not match CITATION.cff")

    if failures:
        print("Version metadata validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Validated release metadata for v{version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
