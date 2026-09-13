#!/usr/bin/env python3
"""Validate the structure of behavioral evaluation contracts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEADING = re.compile(r"^## (\d+)\. .+$", re.MULTILINE)
RUN_HEADINGS = (
    "## Run context",
    "## Results",
    "## Corrective change",
    "## Residual limitations",
)


def main() -> int:
    path = ROOT / "evals" / "scenarios.md"
    text = path.read_text(encoding="utf-8")
    matches = list(HEADING.finditer(text))
    failures: list[str] = []
    numbers = [int(match.group(1)) for match in matches]
    if numbers != list(range(1, len(numbers) + 1)):
        failures.append(f"scenario numbering is not continuous: {numbers}")
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[match.end() : end]
        if not re.search(r"^Prompt: `.+`$", section, re.MULTILINE):
            failures.append(f"scenario {match.group(1)} lacks one inline-code Prompt")
        if not re.search(r"^Expected invariants: .+", section, re.MULTILINE):
            failures.append(f"scenario {match.group(1)} lacks Expected invariants")
    if not matches:
        failures.append("no behavioral scenarios found")

    run_files = sorted((ROOT / "evals" / "runs").glob("*.md"))
    if not run_files:
        failures.append("no behavioral forward-test reports found")
    for run_file in run_files:
        run_text = run_file.read_text(encoding="utf-8")
        for heading in RUN_HEADINGS:
            if heading not in run_text:
                failures.append(f"{run_file.name} lacks {heading}")
    if failures:
        print("Behavioral evaluation contract validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    report_label = "report" if len(run_files) == 1 else "reports"
    print(
        f"Validated {len(matches)} behavioral evaluation contracts and "
        f"{len(run_files)} forward-test {report_label}; "
        "this structural check does not run or score a model."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
