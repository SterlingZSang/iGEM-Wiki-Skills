# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added

- A compact delivery contract across all six skills covering the intended artifact, authorized scope, and observable completion condition.
- A work-loop closure that separates delivered artifacts, unfinished scope, evidence limits, verification, and the most useful next input or action.
- Behavioral scenarios for implementation scope, mid-task changes, evidence-bounded handoff, and small requests that should skip ceremony.
- A recorded independent forward-test report covering all six skills, including one observed failure, its corrective change, and a passing retest.

### Changed

- Repository validation now requires every skill to preserve the preflight, delivery-contract, and work-loop closure contracts; evaluation validation also checks the structure of committed forward-test reports.

## [0.9.0] - 2026-09-13

### Added

- A progressive input-preflight contract across all six skills that reports discovered context, minimum missing inputs, optional confidence boosters, and starting assumptions before substantial work.
- Domain-specific input guidance for story, wet-lab, Model, Human Practices, implementation, and whole-wiki tasks.
- Behavioral scenarios for incomplete requests and complete requests that should proceed without questionnaire friction.

### Changed

- Default skill prompts now ask the agent to inspect available materials before identifying missing inputs.
- Intake guidance distinguishes genuinely blocking information from optional evidence and forbids asking users to re-provide inspectable workspace context.

## [0.8.0] - 2026-09-09

### Added

- A module-level Model corpus with 34 inspected methods across 11 contrasting pages and every year from 2021 through 2025.
- Controlled parameter-provenance, evidence-scope, and reproduction-path labels with biological questions, method summaries, project decisions, and explicit limitations.
- A generated module evidence index and query filters for module text, parameter provenance, evidence scope, and reproduction path.
- Validation that every module belongs to an inspected Model page and cannot exceed its parent page taxonomy.
- A benchmark-year coverage guard that prevents the module layer from regressing to endpoint-only sampling.
- Behavioral and deterministic tests for evidence-fit module retrieval and page/module taxonomy consistency.

### Changed

- Model precedent research now starts with comparable modules and falls back to page-level taxonomy for architecture or uncovered methods.
- The page-level taxonomy for five deep-read pages now acts as a verified superset of their inspected modules.

## [0.7.1] - 2026-09-09

### Added

- Repeatable `--exclude` paths and Markdown output for the static Wiki auditor.
- Optional allowlisted external evidence-link checks with bounded timeouts and redirect controls.
- Tests for exclusions, Markdown reports, evidence-link allowlisting, and HTTPS path handling.

### Changed

- Reclassified the rendered 2025 Heidelberg, Munich, and SUSTech-BIO Model pages using visible method, data, validation, and decision evidence instead of conservative unknown labels.
- Expanded the corresponding exact-page review notes with model-specific strengths and limitations.
- Pinned GitHub Actions dependencies to full commit hashes.

## [0.7.0] - 2026-09-09

### Added

- Controlled Model precedent metadata for archetype, validation type, data source, and project decision across all 14 reviewed Model pages.
- A generated Model taxonomy index and token-aware corpus queries for evidence-fit precedent retrieval.
- Seven targeted exact-page reviews that close the remaining thin Awards, Experiments, Parts, Notebook, Sustainability, Implementation, and Entrepreneurship functions.
- Static Wiki checks for missing local assets, heading-level jumps, machine-local paths, figures without captions, and caller-supplied required routes.
- Behavioral scenarios and deterministic tests for taxonomy retrieval and the expanded static-audit contract.

### Changed

- Model precedent selection now starts from scientific need instead of recency alone and explicitly permits `unclear` when a classification is not supported.
- All maintained core page functions now have at least two exact-page reviews across the 2021–2025 corpus.
- The benchmark corpus now contains 101 page reviews while retaining 1,054 official award records and five hash-verified source snapshots.
- Coordinator verification guidance documents the expanded static checker without treating it as browser, accessibility, or scientific proof.

## [0.6.0] - 2026-09-09

### Added

- Full 2021–2025 official Results imports for every mapped award family including the four current Part award families.
- Historical-name mappings for the 2021 Inclusivity, Safety and Security, and Sustainability awards, recovering 42 previously omitted records.
- Eighteen exact-page reviews covering previously thin Description, Awards, Results, Experiments, Notebook, Parts, Education, Inclusivity, Implementation, and Contribution functions.
- Compact reviewed-page indexes and separate full official award ledgers for progressive loading.
- Exact official API input snapshots whose bytes are validated against the source manifest.
- Dependency-free corpus query and read-only static-wiki audit tools.
- Team intake, judging-readiness, production-board, and browser-QA templates.
- Functional-coverage, structured-award-link, progressive-loading, and static-audit evaluation scenarios.
- Release-metadata validation, evaluation-contract validation, deterministic tool tests, and a documented semantic-version release process.

### Changed

- Page reviews now carry a structured primary official award relationship validated against the award inventory.
- Sampling policy now treats page function as an explicit axis without imposing an every-year-by-function quota.
- The corpus source manifest must cover every maintained benchmark year.
- Team slugs imported from official results are normalized to portable URL-safe identifiers.
- Coordinator routing now handles the current Alternative Platform category and keeps Best Presentation outside wiki-page precedent sampling.
- Annual imports now fail when a maintained year's expected award titles disappear instead of silently preserving stale rows.
- Static HTML link checks reject paths and symlink targets that escape the selected audit root.

## [0.5.0] - 2026-09-08

### Added

- 128 official Best Wiki and Best Model records for 2022–2024, bringing the corpus to 739 award-category records.
- 14 inspected pages that close domain-year gaps, bringing the page-review corpus to 76 records.
- A portable benchmark sampling policy with explicit domain-year, award-status, competition-class, and cross-year inference rules.
- Generated year-by-year coverage and reviewed-sample balance tables.

### Changed

- Story and Model award inventories now cover every maintained year rather than 2021/2025 bookends plus selected intervening winners.
- Curated benchmark notes now include the newly inspected cross-year winner and nominee contrasts.
- Corpus validation now rejects missing benchmark years, insufficient domain-year review depth, missing winner or nominee coverage, and missing competition classes.
- The generated coordinator index no longer depends on a repository-external relative link when skills are installed project-locally.

## [0.4.0] - 2026-09-08

### Added

- 312 official 2022–2024 award-category records for Wet Lab, Human Practices, and Implementation, bringing the corpus to 611 records.
- 18 inspected winner and nominee pages across the three expanded domains, bringing page reviews to 62.
- Annual Results API importer and a source manifest containing competition identifiers, retrieval dates, endpoints, and response hashes.
- Curated 2022–2024 comparison tables in the three domain benchmark corpora.
- Evaluation scenarios for API-based corpus updates and client-rendered pages.

### Changed

- Generated corpus indexes now expose official machine-source provenance.
- Repository validation now requires and validates the source manifest and importer.

## [0.3.0] - 2026-09-08

### Added

- Machine-readable award and page-review CSV corpus with a documented schema.
- 299 official award-category records across five wiki domains.
- 44 domain-scoped page-review records with reusable observations and explicit limitations.
- Generated award/page indexes for every domain skill.
- Dependency-free corpus generator and stale-output validation.

### Changed

- Domain skills now use generated indexes as the canonical local award inventory while preserving curated interpretive notes.
- Repository validation and CI now check corpus integrity and generated artifacts.

## [0.2.0] - 2026-09-08

### Added

- Dated 2026 judging, Standard URL, eligibility, and freeze snapshot.
- AI use, scientific-integrity, privacy, verification, and attribution protocol.
- Cross-page Claim-Evidence Register and evidence-maturity vocabulary.
- Seven reusable evidence and documentation templates.
- UI metadata for every skill.
- Dependency-free repository validator and GitHub Actions workflow.
- Behavior-oriented evaluation scenarios for routing, evidence boundaries, current-season compliance, and read-only scope.

### Changed

- Extended the coordinator with competition-phase guidance and current-season routing.
- Strengthened domain instructions for single-case generalization, AI-assisted analysis, Registry dependencies, and 2026 Software eligibility.
- Expanded whole-wiki review checks for AI disclosure, Standard URLs, external artifacts, and pre-freeze compliance.

## [0.1.0] - 2026-09-08

### Added

- Initial coordinator and five domain skills.
- Winner and nominee benchmark corpora.
- Whole-wiki, Model, evidence, UX, and reproducibility checklists.
