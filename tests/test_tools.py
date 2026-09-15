from __future__ import annotations

import csv
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
DOCTOR = ROOT / "igem-wiki" / "scripts" / "doctor.py"
INSTALLER = ROOT / "scripts" / "install_skills.py"
SKILLS = (
    "igem-wiki",
    "igem-wiki-story",
    "igem-wetlab-wiki",
    "igem-model-wiki",
    "igem-hp-wiki",
    "igem-implementation-wiki",
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.importer = load_module("import_annual_results", ROOT / "scripts" / "import_annual_results.py")

    def test_invalid_verification_date_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.importer.validate_date("2026-9-9")

    def test_missing_expected_award_title_is_rejected(self) -> None:
        titles = self.importer.EXPECTED_TITLES_BY_YEAR[2025] - {"Best Model"}
        data = [{"title": title} for title in titles]
        with self.assertRaisesRegex(ValueError, "Best Model"):
            self.importer.validate_award_titles(2025, data)


class EvaluationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.validator = load_module("validate_evals", ROOT / "scripts" / "validate_evals.py")

    def test_empty_forward_report_is_rejected(self) -> None:
        text = """# Empty report
## Run context
- Candidate: candidate
- Evaluator: evaluator
- Mutation boundary: read-only
## Results
## Corrective change
None.
## Residual limitations
None recorded.
"""
        failures = self.validator.validate_run_report("empty.md", text)
        self.assertTrue(any("result row" in failure for failure in failures))


class StaticAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = load_module(
            "audit_static_wiki", ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"
        )

    def run_audit(self, root: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"),
                str(root),
                "--json",
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_local_link_cannot_escape_audit_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = parent / "wiki"
            root.mkdir()
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1><a href="../outside.html#private">x</a></html>',
                encoding="utf-8",
            )
            (parent / "outside.html").write_text(
                '<html lang="en"><title>Outside</title><h1 id="private">Outside</h1></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["errors"], 1)
            self.assertIn("escapes audit root", report["findings"][0]["message"])

    def test_heading_jump_and_missing_figure_caption_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "plot.png").write_bytes(b"png")
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1><h3>Results</h3>'
                '<figure><img src="plot.png" alt="response curve"></figure></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            messages = [item["message"] for item in report["findings"]]
            self.assertIn("heading level jumps from h1 to h3", messages)
            self.assertIn("figure contains a visual but no figcaption", messages)

    def test_machine_local_path_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1>'
                '<img src="/Users/example/Desktop/private.png" alt="private"></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any("machine-local path" in item["message"] for item in report["findings"])
            )

    def test_https_url_is_not_treated_as_a_windows_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1>'
                '<script src="https://cdn.example.org/app.js"></script></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            self.assertFalse(
                any("machine-local path" in item["message"] for item in report["findings"])
            )

    def test_required_route_missing_is_a_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            result, report = self.run_audit(root, "--required-route", "model")
            self.assertEqual(result.returncode, 0)
            self.assertTrue(
                any("required route not found: model" in item["message"] for item in report["findings"])
            )

    def test_excluded_relative_directory_is_not_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            drafts = root / "drafts"
            drafts.mkdir()
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            (drafts / "broken.html").write_text(
                '<html><a href="missing.html">broken</a></html>', encoding="utf-8"
            )
            result, report = self.run_audit(root, "--exclude", "drafts")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["html_files"], 1)

    def test_markdown_report_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                '<html lang="en"><title>Home</title><h1>Home</h1></html>',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "igem-wiki" / "scripts" / "audit_static_wiki.py"),
                    str(root),
                    "--markdown",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("# Static Wiki audit", result.stdout)
            self.assertIn("No findings", result.stdout)

    def test_external_evidence_allowlist(self) -> None:
        self.assertTrue(
            self.audit.allowed_external_evidence_url("https://2025.igem.wiki/example/model")
        )
        self.assertTrue(
            self.audit.allowed_external_evidence_url("https://github.com/example/repository")
        )
        self.assertFalse(
            self.audit.allowed_external_evidence_url("http://github.com/example/repository")
        )
        self.assertFalse(
            self.audit.allowed_external_evidence_url("https://example.com/private")
        )


class ClaimConsistencyAuditTests(unittest.TestCase):
    def run_audit(self, root: Path, *extra: str) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "igem-wiki" / "scripts" / "audit_claim_consistency.py"),
                str(root),
                "--json",
                *extra,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_conflicting_numbers_are_review_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "results.html").write_text(
                "<p>SVN protein yield improved for the optimized construct by 12%.</p>",
                encoding="utf-8",
            )
            (root / "award.html").write_text(
                "<p>SVN protein yield improved for the optimized construct by 98%.</p>",
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(any("numeric" in item["types"] for item in report["findings"]))

    def test_summary_number_without_owner_is_a_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "award.html").write_text(
                "<div><strong>98%</strong><span>Model prediction correlation with experiment</span></div>",
                encoding="utf-8",
            )
            (root / "model.html").write_text(
                "<p>The model prediction has no matched experiment for correlation analysis.</p>",
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any("unowned-summary" in item["types"] for item in report["findings"])
            )

    def test_summary_number_with_matching_owner_is_not_unowned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            sentence = "SVN protein yield improved for the optimized construct by 12%."
            (root / "award.html").write_text(f"<p>{sentence}</p>", encoding="utf-8")
            (root / "results.html").write_text(f"<p>{sentence}</p>", encoding="utf-8")
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            self.assertFalse(
                any("unowned-summary" in item["types"] for item in report["findings"])
            )

    def test_conflicting_maturity_is_a_review_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "implementation.html").write_text(
                "<p>The integrated protein design platform is planned for controlled deployment.</p>",
                encoding="utf-8",
            )
            (root / "award.html").write_text(
                "<p>The integrated protein design platform is validated for controlled deployment.</p>",
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["candidates"], 1)
            self.assertIn("maturity", report["findings"][0]["types"])

    def test_unrelated_claims_are_not_paired(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "education.html").write_text(
                "<p>Our workshop reached 150 participants across partner schools.</p>",
                encoding="utf-8",
            )
            (root / "results.html").write_text(
                "<p>SVN protein yield improved for the optimized construct by 12%.</p>",
                encoding="utf-8",
            )
            result, report = self.run_audit(root)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["candidates"], 0)

    def test_section_number_is_not_reinterpreted_as_a_protein_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "award.html").write_text(
                "<p>98% correlation between model predictions and experimental results</p>",
                encoding="utf-8",
            )
            (root / "engineering.html").write_text(
                "<h2>Cycle 3 Complex Multi-Disulfide Protein Validation</h2>",
                encoding="utf-8",
            )
            _result, report = self.run_audit(root)
            paired = [item for item in report["findings"] if item["right"] is not None]
            self.assertEqual(paired, [])

    def test_excluded_directory_is_not_compared(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            drafts = root / "drafts"
            drafts.mkdir()
            (root / "results.html").write_text(
                "<p>SVN protein yield improved for the optimized construct by 12%.</p>",
                encoding="utf-8",
            )
            (drafts / "award.html").write_text(
                "<p>SVN protein yield improved for the optimized construct by 98%.</p>",
                encoding="utf-8",
            )
            result, report = self.run_audit(root, "--exclude", "drafts")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["html_files"], 1)
            self.assertEqual(report["candidates"], 0)

    def test_markdown_mode_discloses_review_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "index.html").write_text(
                "<p>The integrated protein design platform is planned for controlled deployment.</p>",
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "igem-wiki" / "scripts" / "audit_claim_consistency.py"),
                    str(root),
                    "--markdown",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("# Cross-page claim consistency audit", result.stdout)
            self.assertIn("not proof of contradiction", result.stdout)


class CorpusQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_module("build_corpus", ROOT / "scripts" / "build_corpus.py")

    def test_model_metadata_token_filter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "query_corpus.py"),
                "model-metadata",
                "--model-archetype",
                "stochastic",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        rows = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertTrue(rows)
        self.assertTrue(
            all("stochastic" in row["model_archetype"].split(";") for row in rows)
        )

    def test_model_module_evidence_filter(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "query_corpus.py"),
                "model-modules",
                "--project-decision",
                "stopping-policy",
                "--evidence-scope",
                "validated-with-team-data",
                "--format",
                "json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        rows = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0)
        self.assertEqual([row["module_id"] for row in rows], ["flocculation-timing"])
        self.assertEqual(rows[0]["team"], "NUS-Singapore")

    def test_model_module_cannot_exceed_page_taxonomy(self) -> None:
        def rows(name: str) -> list[dict[str, str]]:
            with (ROOT / "corpus" / name).open(newline="", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))

        reviews = rows("page_reviews.csv")
        metadata = rows("model_review_metadata.csv")
        modules = rows("model_modules.csv")
        changed = [dict(row) for row in modules]
        changed[0]["model_archetype"] = "data-driven-ml"
        with self.assertRaisesRegex(ValueError, "exceeds its page taxonomy"):
            self.builder.validate_model_modules(changed, reviews, metadata)

    def test_model_module_corpus_requires_each_benchmark_year(self) -> None:
        def rows(name: str) -> list[dict[str, str]]:
            with (ROOT / "corpus" / name).open(newline="", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))

        reviews = rows("page_reviews.csv")
        metadata = rows("model_review_metadata.csv")
        modules = [row for row in rows("model_modules.csv") if row["year"] != "2022"]
        with self.assertRaisesRegex(ValueError, "missing benchmark years 2022"):
            self.builder.validate_model_modules(modules, reviews, metadata)

    def test_corpus_reader_rejects_extra_csv_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            original = self.builder.CORPUS
            try:
                self.builder.CORPUS = Path(temporary)
                (Path(temporary) / "broken.csv").write_text(
                    "first,second\none,two,unexpected\n", encoding="utf-8"
                )
                with self.assertRaisesRegex(ValueError, "too many CSV fields"):
                    self.builder.read_csv("broken.csv", ("first", "second"))
            finally:
                self.builder.CORPUS = original


class SkillDoctorTests(unittest.TestCase):
    def run_doctor(
        self, skill_root: Path, *extra: str
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [sys.executable, str(DOCTOR), str(skill_root), "--json", *extra],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def copy_skills(self, target: Path, skills: tuple[str, ...] = SKILLS) -> None:
        target.mkdir(parents=True)
        for skill in skills:
            shutil.copytree(ROOT / skill, target / skill)

    def test_coordinator_requires_missing_siblings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-wiki",))
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["expected_mode"], "full-collection")
            self.assertEqual(set(report["missing_skills"]), set(SKILLS[1:]))
            self.assertTrue(
                any(item["code"] == "coordinator-sibling-missing" for item in report["issues"])
            )

    def test_standalone_domain_skill_is_healthy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["expected_mode"], "standalone-domain")
            self.assertEqual(report["present_skills"], ["igem-model-wiki"])
            self.assertEqual(report["installed_version"], "1.0.0")
            self.assertEqual(report["issues"], [])

    def test_direct_skill_directory_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki", "igem-wetlab-wiki"))
            with (skill_root / "igem-wetlab-wiki" / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\nunrelated local change\n")
            result, report = self.run_doctor(skill_root / "igem-model-wiki")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(Path(report["root"]).resolve(), skill_root.resolve())
            self.assertEqual(report["present_skills"], ["igem-model-wiki"])
            self.assertEqual(report["selected_skill"], "igem-model-wiki")

    def test_source_comparison_accepts_exact_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root)
            result, report = self.run_doctor(
                skill_root, "--source", str(ROOT), "--as-of", "2026-09-15"
            )
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report["issues"], [])
            self.assertEqual(report["source_version"], (ROOT / "VERSION").read_text().strip())

    def test_source_comparison_reports_stale_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            with (skill_root / "igem-model-wiki" / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\nlocal change\n")
            result, report = self.run_doctor(skill_root, "--source", str(ROOT))
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any(item["code"] == "installed-file-stale" for item in report["issues"])
            )

    def test_valid_default_checkpoint_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            skill_root = temporary_root / "skills"
            project_root = temporary_root / "project"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            checkpoint = project_root / ".igem-wiki" / "checkpoint.md"
            checkpoint.parent.mkdir(parents=True)
            shutil.copyfile(
                ROOT / "igem-wiki" / "assets" / "templates" / "resume-checkpoint.md",
                checkpoint,
            )
            result, report = self.run_doctor(
                skill_root, "--project-root", str(project_root)
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(report["checkpoint"]["present"])
            self.assertEqual(report["checkpoint"]["issues"], [])

    def test_checkpoint_secret_is_reported_without_echo(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            skill_root = temporary_root / "skills"
            project_root = temporary_root / "project"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            checkpoint = project_root / ".igem-wiki" / "checkpoint.md"
            checkpoint.parent.mkdir(parents=True)
            checkpoint.write_text(
                "# Wiki work checkpoint\n## Context\npassword=verysecret\n",
                encoding="utf-8",
            )
            result, report = self.run_doctor(
                skill_root, "--project-root", str(project_root)
            )
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("verysecret", result.stdout)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("checkpoint-possible-secret", codes)
            self.assertIn("checkpoint-heading-missing", codes)

    def test_local_link_cannot_escape_skill_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            skill_root = temporary_root / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            (temporary_root / "outside.md").write_text("outside\n", encoding="utf-8")
            with (skill_root / "igem-model-wiki" / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\n[private](../../outside.md)\n")
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any(item["code"] == "local-link-escapes-root" for item in report["issues"])
            )

    def test_symbolic_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            skill_root = temporary_root / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            outside = temporary_root / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            (skill_root / "igem-model-wiki" / "references" / "linked.txt").symlink_to(outside)
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any(item["code"] == "symlink-not-portable" for item in report["issues"])
            )

    def test_symbolic_link_skill_root_is_not_followed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            real_root = temporary_root / "real-skills"
            self.copy_skills(real_root, ("igem-model-wiki",))
            linked_root = temporary_root / "linked-skills"
            linked_root.symlink_to(real_root, target_is_directory=True)
            result, report = self.run_doctor(linked_root)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(report["present_skills"], [])
            self.assertTrue(
                any(
                    item["code"] == "skill-root-symlink-not-allowed"
                    for item in report["issues"]
                )
            )

    def test_stale_season_is_warning_not_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root)
            result, report = self.run_doctor(skill_root, "--as-of", "2026-12-01")
            self.assertEqual(result.returncode, 0)
            warnings = [item for item in report["issues"] if item["severity"] == "warning"]
            self.assertTrue(any(item["code"] == "season-snapshot-stale" for item in warnings))

    def test_mixed_installed_versions_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki", "igem-wetlab-wiki"))
            manifest_path = skill_root / "igem-wetlab-wiki" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["version"] = "0.9.0"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(
                any(item["code"] == "installed-version-mismatch" for item in report["issues"])
            )

    def test_invalid_manifest_metadata_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            skill_root = Path(temporary) / "skills"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            manifest_path = skill_root / "igem-model-wiki" / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["schema_version"] = 99
            manifest["collection"] = "different-collection"
            manifest["version"] = "version-one"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            result, report = self.run_doctor(skill_root)
            self.assertEqual(result.returncode, 1)
            codes = {item["code"] for item in report["issues"]}
            self.assertIn("manifest-schema-unsupported", codes)
            self.assertIn("manifest-collection-mismatch", codes)
            self.assertIn("manifest-version-invalid", codes)

    def test_checkpoint_symlink_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            skill_root = temporary_root / "skills"
            project_root = temporary_root / "project"
            self.copy_skills(skill_root, ("igem-model-wiki",))
            outside = temporary_root / "outside.md"
            outside.write_text("password=verysecret\n", encoding="utf-8")
            checkpoint = project_root / ".igem-wiki" / "checkpoint.md"
            checkpoint.parent.mkdir(parents=True)
            checkpoint.symlink_to(outside)
            result, report = self.run_doctor(
                skill_root, "--project-root", str(project_root)
            )
            self.assertEqual(result.returncode, 1)
            self.assertNotIn("verysecret", result.stdout)
            self.assertTrue(
                any(
                    item["code"] == "checkpoint-symlink-not-allowed"
                    for item in report["issues"]
                )
            )


class SkillInstallerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.installer = load_module("install_skills", INSTALLER)

    def run_installer(
        self, target: Path, *extra: str
    ) -> tuple[subprocess.CompletedProcess[str], dict]:
        result = subprocess.run(
            [sys.executable, str(INSTALLER), str(target), "--json", *extra],
            capture_output=True,
            text=True,
            check=False,
        )
        return result, json.loads(result.stdout)

    def test_preview_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills"
            result, report = self.run_installer(
                target, "--skill", "igem-model-wiki"
            )
            self.assertEqual(result.returncode, 0)
            self.assertFalse(target.exists())
            self.assertFalse(report["applied"])
            self.assertEqual(report["changes"][0]["action"], "install")

    def test_source_manifest_schema_and_collection_are_required(self) -> None:
        manifest_path = ROOT / "igem-model-wiki" / "manifest.json"
        original = json.loads(manifest_path.read_text(encoding="utf-8"))
        for field, value in (("schema_version", 99), ("collection", "other")):
            changed = dict(original)
            changed[field] = value
            with mock.patch.object(
                self.installer,
                "read_manifest",
                return_value=changed,
            ):
                with self.assertRaisesRegex(ValueError, "source manifest does not match"):
                    self.installer.validate_source(["igem-model-wiki"])

    def test_apply_installs_selected_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills"
            result, report = self.run_installer(
                target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(report["applied"])
            self.assertTrue((target / "igem-model-wiki" / "SKILL.md").is_file())
            self.assertFalse((target / "igem-wiki").exists())
            doctor = subprocess.run(
                [sys.executable, str(DOCTOR), str(target), "--source", str(ROOT)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(doctor.returncode, 0, doctor.stdout + doctor.stderr)

    def test_update_backs_up_and_removes_extra_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills"
            first, _ = self.run_installer(
                target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(first.returncode, 0)
            skill_file = target / "igem-model-wiki" / "SKILL.md"
            with skill_file.open("a", encoding="utf-8") as handle:
                handle.write("\nlocal edit\n")
            (target / "igem-model-wiki" / "extra.txt").write_text(
                "extra\n", encoding="utf-8"
            )
            result, report = self.run_installer(
                target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(result.returncode, 0)
            self.assertIsNotNone(report["backup"])
            backup = Path(report["backup"]) / "igem-model-wiki"
            self.assertTrue((backup / "extra.txt").is_file())
            self.assertIn("local edit", (backup / "SKILL.md").read_text(encoding="utf-8"))
            self.assertFalse((target / "igem-model-wiki" / "extra.txt").exists())
            self.assertEqual(
                skill_file.read_bytes(), (ROOT / "igem-model-wiki" / "SKILL.md").read_bytes()
            )

    def test_symbolic_link_target_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            real_target = temporary_root / "real"
            real_target.mkdir()
            linked_target = temporary_root / "linked"
            linked_target.symlink_to(real_target, target_is_directory=True)
            result, report = self.run_installer(
                linked_target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("symbolic link", report["error"])

    def test_symbolic_link_backup_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            target = temporary_root / "skills"
            first, _ = self.run_installer(
                target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(first.returncode, 0)
            with (target / "igem-model-wiki" / "SKILL.md").open("a", encoding="utf-8") as handle:
                handle.write("\nlocal edit\n")
            outside = temporary_root / "outside-backups"
            outside.mkdir()
            (target / ".igem-wiki-backups").symlink_to(outside, target_is_directory=True)
            result, report = self.run_installer(
                target, "--skill", "igem-model-wiki", "--apply"
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("backup directory", report["error"])
            self.assertIn(
                "local edit",
                (target / "igem-model-wiki" / "SKILL.md").read_text(encoding="utf-8"),
            )

    def test_failed_multi_skill_update_rolls_back_prior_replacements(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "skills"
            target.mkdir()
            selected = ["igem-model-wiki", "igem-wetlab-wiki"]
            for skill in selected:
                shutil.copytree(ROOT / skill, target / skill)
                with (target / skill / "SKILL.md").open("a", encoding="utf-8") as handle:
                    handle.write(f"\nold {skill}\n")
            version = self.installer.validate_source(selected)
            report = self.installer.plan_install(target, selected, version)
            original_replace = self.installer.os.replace

            def fail_on_second_new(source, destination):
                source_path = Path(source)
                if source_path.parent.name == "new" and source_path.name == "igem-wetlab-wiki":
                    raise OSError("simulated replacement failure")
                return original_replace(source, destination)

            with mock.patch.object(self.installer.os, "replace", side_effect=fail_on_second_new):
                with self.assertRaisesRegex(OSError, "simulated replacement failure"):
                    self.installer.apply_plan(report)
            for skill in selected:
                self.assertIn(
                    f"old {skill}",
                    (target / skill / "SKILL.md").read_text(encoding="utf-8"),
                )


if __name__ == "__main__":
    unittest.main()
