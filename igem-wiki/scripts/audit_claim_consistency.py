#!/usr/bin/env python3
"""Find review candidates for conflicting claims across static HTML pages."""

from __future__ import annotations

import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


SKIP_DIRS = {".git", "node_modules", "dist", "build", ".cache", "templates"}
SKIP_TAGS = {"script", "style", "noscript", "template", "nav", "footer"}
BLOCK_TAGS = {"p", "li", "td", "th", "figcaption", "blockquote"} | {
    f"h{level}" for level in range(1, 7)
}
CONTAINER_TAGS = {"section", "article", "div"}
MAX_CONTEXT_CHARS = 800
SUMMARY_PAGE_NAMES = {
    "award.html",
    "awards.html",
    "description.html",
    "home.html",
    "index.html",
    "judging.html",
    "project-description.html",
}
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{2,}|[\u4e00-\u9fff]{2,}")
STATUS_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]*")
UNIT_PATTERN = (
    r"%|percent(?:age)?|fold|x|×|aa|bp|kbp?|kda|da|nm|[µμu]m|mm|cm|"
    r"ml|[µμu]l|ng|[µμu]g|mg|rpm|od600|r2|r²|sec(?:ond)?s?|min(?:ute)?s?|"
    r"hours?|days?|replicates?|runs?|cycles?|constructs?|proteins?|sequences?|"
    r"participants?|schools?|materials?"
)
NUMBER_RE = re.compile(
    rf"(?<![\w.])(\d+(?:,\d{{3}})*(?:\.\d+)?\+?(?:\s*[-–]\s*\d+(?:,\d{{3}})*(?:\.\d+)?\+?)?)\s*(?:[-–]\s*)?(?:(?:[A-Za-z][A-Za-z-]*\s+){{1,2}}(?=(?:participants?|schools?|materials?)\b))?({UNIT_PATTERN})(?!\w)",
    re.IGNORECASE,
)
STRONG_TERMS = {
    "achieved",
    "completed",
    "confirmed",
    "demonstrated",
    "demonstrates",
    "improved",
    "increased",
    "proven",
    "proves",
    "reduced",
    "successful",
    "successfully",
    "validated",
    "verified",
}
TENTATIVE_TERMS = {
    "expected",
    "future",
    "hypothesis",
    "hypothetical",
    "illustrative",
    "intended",
    "pending",
    "planned",
    "preliminary",
    "proposed",
    "provisional",
    "placeholder",
    "reserved",
    "simulated",
    "unvalidated",
}
NEGATORS = {"lack", "lacks", "lacking", "missing", "no", "not", "without"}
WORD_ALIASES = {
    "constructs": "construct",
    "cycles": "cycle",
    "experimental": "experiment",
    "experiments": "experiment",
    "materials": "material",
    "modeling": "model",
    "modelling": "model",
    "models": "model",
    "outcomes": "outcome",
    "participants": "participant",
    "predictions": "prediction",
    "proteins": "protein",
    "schools": "school",
    "simulations": "simulation",
}
STOPWORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "can",
    "could",
    "does",
    "each",
    "for",
    "from",
    "had",
    "has",
    "have",
    "into",
    "its",
    "may",
    "more",
    "not",
    "our",
    "page",
    "should",
    "than",
    "that",
    "the",
    "their",
    "then",
    "these",
    "this",
    "those",
    "through",
    "under",
    "using",
    "was",
    "were",
    "which",
    "will",
    "with",
    "would",
}


class VisibleBlockParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.active_tag: str | None = None
        self.active_line = 0
        self.active_text: list[str] = []
        self.containers: list[dict[str, object]] = []
        self.blocks: list[tuple[int, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip_depth:
            if tag in SKIP_TAGS:
                self.skip_depth += 1
            return
        if tag in SKIP_TAGS:
            self.skip_depth = 1
            return
        if tag in CONTAINER_TAGS:
            self.containers.append({"tag": tag, "line": self.getpos()[0], "text": []})
        if tag in BLOCK_TAGS:
            self.flush()
            self.active_tag = tag
            self.active_line = self.getpos()[0]

    def handle_endtag(self, tag: str) -> None:
        if self.skip_depth:
            if tag in SKIP_TAGS:
                self.skip_depth -= 1
            return
        if tag == self.active_tag:
            self.flush()
        if tag in CONTAINER_TAGS and self.containers and self.containers[-1]["tag"] == tag:
            container = self.containers.pop()
            text = " ".join(" ".join(container["text"]).split())
            if text and len(text) <= MAX_CONTEXT_CHARS:
                self.blocks.append((int(container["line"]), text))

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        if self.active_tag:
            self.active_text.append(data)
        for container in self.containers:
            container["text"].append(data)

    def close(self) -> None:
        super().close()
        self.flush()

    def flush(self) -> None:
        if self.active_tag:
            text = " ".join(" ".join(self.active_text).split())
            if text:
                self.blocks.append((self.active_line, text))
        self.active_tag = None
        self.active_line = 0
        self.active_text = []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="directory containing static HTML files")
    parser.add_argument("--no-fail", action="store_true", help="always return success after reporting")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    output.add_argument("--markdown", action="store_true", help="emit a Markdown review report")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="exclude a relative file or directory; repeat as needed",
    )
    parser.add_argument(
        "--min-shared-keywords",
        type=int,
        default=3,
        metavar="COUNT",
        help="minimum shared content words for a candidate pair (default: 3)",
    )
    parser.add_argument(
        "--similarity",
        type=float,
        default=0.55,
        metavar="RATIO",
        help="minimum keyword containment ratio from 0 to 1 (default: 0.55)",
    )
    parser.add_argument(
        "--max-findings",
        type=int,
        default=200,
        metavar="COUNT",
        help="maximum candidate pairs to report (default: 200)",
    )
    return parser.parse_args()


def exclusion_prefixes(values: list[str]) -> tuple[tuple[str, ...], ...]:
    prefixes = []
    for value in values:
        path = Path(unquote(value))
        if path.is_absolute() or ".." in path.parts or not path.parts:
            raise ValueError(f"exclude path must be a safe relative path: {value}")
        prefixes.append(path.parts)
    return tuple(prefixes)


def html_files(root: Path, excluded: tuple[tuple[str, ...], ...]) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*.html")
        if not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
        and not any(
            path.relative_to(root).parts[: len(prefix)] == prefix for prefix in excluded
        )
        and path.resolve().is_relative_to(root)
    )


def normalize_number(match: re.Match[str]) -> str:
    value = match.group(1).replace(",", "").replace("–", "-").replace(" ", "")
    unit = match.group(2).casefold().replace("μ", "u").replace("µ", "u").replace("×", "x")
    if unit.startswith("percent"):
        unit = "%"
    return f"{value}{unit}"


def normalize_keyword(token: str) -> str:
    word = token.casefold()
    if word in WORD_ALIASES:
        return WORD_ALIASES[word]
    if word.endswith("s") and len(word) > 5 and not word.endswith("ss"):
        return word[:-1]
    return word


def content_keywords(text: str) -> frozenset[str]:
    excluded = STOPWORDS | STRONG_TERMS | TENTATIVE_TERMS
    return frozenset(
        normalize_keyword(token)
        for token in WORD_RE.findall(text)
        if normalize_keyword(token) not in excluded
    )


def status_polarity(text: str) -> str | None:
    words = [token.casefold() for token in STATUS_WORD_RE.findall(text)]
    strong = False
    tentative = bool(set(words) & TENTATIVE_TERMS)
    for index, word in enumerate(words):
        if word not in STRONG_TERMS:
            continue
        if set(words[max(0, index - 14) : index]) & NEGATORS:
            tentative = True
        else:
            strong = True
    if strong and not tentative:
        return "strong"
    if tentative and not strong:
        return "tentative"
    return None


def page_blocks(root: Path, path: Path) -> list[dict[str, object]]:
    parser = VisibleBlockParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    relative = str(path.relative_to(root))
    blocks = []
    seen: set[tuple[int, str]] = set()
    for line, text in sorted(parser.blocks, key=lambda item: len(item[1])):
        key = (line, text)
        if key in seen:
            continue
        seen.add(key)
        numbers = frozenset(normalize_number(match) for match in NUMBER_RE.finditer(text))
        polarity = status_polarity(text)
        if not numbers and not polarity:
            continue
        blocks.append(
            {
                "file": relative,
                "line": line,
                "text": text,
                "numbers": numbers,
                "polarity": polarity,
                "keywords": content_keywords(text),
            }
        )
    return blocks


def public_block(block: dict[str, object]) -> dict[str, object]:
    return {
        "file": block["file"],
        "line": block["line"],
        "text": block["text"],
        "numbers": sorted(block["numbers"]),
        "polarity": block["polarity"],
    }


def is_summary_page(block: dict[str, object]) -> bool:
    return Path(str(block["file"])).name.casefold() in SUMMARY_PAGE_NAMES


def unowned_summary_findings(
    blocks: list[dict[str, object]], min_shared: int
) -> list[dict[str, object]]:
    findings = []
    seen: set[tuple[str, tuple[str, ...], tuple[str, ...]]] = set()
    summary_min_shared = min(2, min_shared)
    for block in sorted(blocks, key=lambda item: len(str(item["text"]))):
        if (
            not is_summary_page(block)
            or not block["numbers"]
            or len(block["keywords"]) < summary_min_shared
            or len(str(block["text"])) > 300
        ):
            continue
        if any(
            item["left"]["file"] == block["file"]
            and set(item["left"]["numbers"]).issubset(block["numbers"])
            and str(item["left"]["text"]) in str(block["text"])
            for item in findings
        ):
            continue
        signature = (
            str(block["file"]),
            tuple(sorted(block["numbers"])),
            tuple(sorted(block["keywords"])),
        )
        if signature in seen:
            continue
        seen.add(signature)
        supported = False
        best_shared: frozenset[str] = frozenset()
        for other in blocks:
            if other["file"] == block["file"] or is_summary_page(other):
                continue
            if not (block["numbers"] & other["numbers"]):
                continue
            shared = block["keywords"] & other["keywords"]
            if len(shared) > len(best_shared):
                best_shared = shared
            if len(shared) >= summary_min_shared:
                supported = True
                break
        if not supported:
            findings.append(
                {
                    "types": ["unowned-summary"],
                    "left": public_block(block),
                    "right": None,
                    "shared_keywords": sorted(best_shared),
                    "similarity": 0.0,
                }
            )
    return findings


def candidate_findings(
    blocks: list[dict[str, object]], min_shared: int, similarity: float, maximum: int
) -> list[dict[str, object]]:
    findings = []
    for left_index, left in enumerate(blocks):
        left_keywords = left["keywords"]
        if len(left_keywords) < min_shared:
            continue
        for right in blocks[left_index + 1 :]:
            if left["file"] == right["file"]:
                continue
            right_keywords = right["keywords"]
            if len(right_keywords) < min_shared:
                continue
            shared = left_keywords & right_keywords
            if len(shared) < min_shared:
                continue
            containment = len(shared) / min(len(left_keywords), len(right_keywords))
            if containment < similarity:
                continue

            kinds = []
            if left["numbers"] and right["numbers"] and left["numbers"] != right["numbers"]:
                kinds.append("numeric")
            if {left["polarity"], right["polarity"]} == {"strong", "tentative"}:
                kinds.append("maturity")
            if not kinds:
                continue
            findings.append(
                {
                    "types": kinds,
                    "left": public_block(left),
                    "right": public_block(right),
                    "shared_keywords": sorted(shared),
                    "similarity": round(containment, 3),
                }
            )
            if len(findings) >= maximum:
                return findings
    return findings


def markdown_report(report: dict[str, object]) -> str:
    lines = [
        "# Cross-page claim consistency audit",
        "",
        f"Root: `{report['root']}`",
        "",
        f"Checked **{report['html_files']}** HTML files and **{report['claim_blocks']}** claim-bearing blocks; found **{report['candidates']} review candidates**.",
        "",
    ]
    for index, item in enumerate(report["findings"], start=1):
        kinds = ", ".join(item["types"])
        left = item["left"]
        right = item["right"]
        lines.extend([f"## {index}. {kinds} candidate", ""])
        lines.append(f"- `{left['file']}:{left['line']}` — {left['text']}")
        if right:
            lines.append(f"- `{right['file']}:{right['line']}` — {right['text']}")
            lines.append(f"- Shared context: {', '.join(item['shared_keywords'])}")
        else:
            lines.append(
                "- No non-summary page repeats the same number with sufficient shared context; identify the canonical evidence owner before publishing it as a headline claim."
            )
        lines.append("")
    if not report["findings"]:
        lines.extend(["No review candidates found.", ""])
    lines.append(
        "> Candidates are lexical review prompts, not proof of contradiction or scientific invalidity. Check conditions, units, evidence owners, and source artifacts before changing a claim."
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {root}")
    if args.min_shared_keywords < 1:
        raise SystemExit("--min-shared-keywords must be at least 1")
    if not 0 < args.similarity <= 1:
        raise SystemExit("--similarity must be greater than 0 and at most 1")
    if args.max_findings < 1:
        raise SystemExit("--max-findings must be at least 1")
    try:
        excluded = exclusion_prefixes(args.exclude)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    pages = html_files(root, excluded)
    blocks = [block for path in pages for block in page_blocks(root, path)]
    unowned = unowned_summary_findings(blocks, min_shared=args.min_shared_keywords)
    paired = candidate_findings(
        blocks,
        min_shared=args.min_shared_keywords,
        similarity=args.similarity,
        maximum=args.max_findings,
    )
    all_findings = unowned + paired
    findings = all_findings[: args.max_findings]
    report = {
        "root": str(root),
        "html_files": len(pages),
        "claim_blocks": len(blocks),
        "candidates": len(findings),
        "truncated": len(all_findings) > args.max_findings or len(paired) == args.max_findings,
        "findings": findings,
    }

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    elif args.markdown:
        print(markdown_report(report), end="")
    else:
        print(
            f"Checked {len(pages)} HTML files and {len(blocks)} claim-bearing blocks; "
            f"found {len(findings)} review candidates."
        )
        for item in findings:
            left = item["left"]
            right = item["right"]
            if right:
                print(
                    f"- {','.join(item['types'])}: {left['file']}:{left['line']} <-> "
                    f"{right['file']}:{right['line']}"
                )
            else:
                print(f"- unowned-summary: {left['file']}:{left['line']}")
        print("Candidates require human review; they are not proof of contradiction.")

    return 0 if args.no_fail or not findings else 1


if __name__ == "__main__":
    raise SystemExit(main())
