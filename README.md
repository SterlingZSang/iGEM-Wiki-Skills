# iGEM Wiki Skills

A modular Codex skill collection for researching, planning, writing, implementing, and auditing evidence-led iGEM team wikis.

Current release: **v0.9.0**

## Skills

| Skill | Scope |
|---|---|
| `igem-wiki` | Whole-wiki architecture, current-season compliance, cross-page claims, AI integrity, and task routing |
| `igem-wiki-story` | Home, Description, Awards, navigation, and project narrative |
| `igem-wetlab-wiki` | Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, and Notebook |
| `igem-model-wiki` | Modeling, equations, computational evidence, validation, and reproducibility |
| `igem-hp-wiki` | Human Practices, Education, Inclusivity, Sustainability, ethics, and stakeholder integration |
| `igem-implementation-wiki` | Implementation, Safety, Entrepreneurship, Hardware, Software, and Contribution |

## What v0.9.0 adds

Release v0.9.0 adds a progressive input preflight across all six skills, while retaining the v0.8.0 module-level Model evidence corpus.

- a short readiness note that distinguishes discovered context, minimum missing inputs, optional confidence boosters, and starting assumptions;
- domain-specific input guidance for whole-wiki, story, wet-lab, Model, Human Practices, and implementation work;
- direct starts for complete requests instead of generic questionnaires or repeated requests for inspectable workspace context;
- behavioral scenarios for both underspecified and complete requests, plus a repository guard for the shared preflight contract.

The v0.8.0 evidence and tooling foundation remains included:

- a machine-readable benchmark corpus with **1,054 official award records** and **101 domain-scoped page-review records**;
- controlled taxonomy for all 14 reviewed Model pages across archetype, validation type, data source, and project decision;
- **34 inspected Model modules across every year from 2021 through 2025**, recording biological question, method, parameter provenance, evidence scope, reproduction path, project decision, and a concrete limitation;
- evidence-fit Model precedent queries, so scientific relevance comes before recency or award prestige;
- at least two reviewed examples for every maintained core page function, including Awards, Experiments, Parts, Notebook, Sustainability, Implementation, and Entrepreneurship;
- expanded static-site checks for local assets, heading hierarchy, machine-local paths, figure captions, and caller-supplied required routes;
- complete mapped 2021–2025 award-family imports with explicit historical-title contracts, including 42 recovered 2021 records;
- exact official API JSON snapshots verified against the source manifest hashes;
- structured primary award links for page reviews and visible year, class, status, and page-function coverage;
- compact reviewed-page indexes separated from full official award ledgers for progressive loading;
- dependency-free corpus query and read-only static-site audit tools;
- four whole-wiki intake, production, judging-readiness, and browser-QA templates;
- deterministic regression tests plus release-version and evaluation-contract validation;
- a documented semantic-version release process that separates descriptive development commits from versioned releases.

The earlier evidence templates, 2026 judging snapshot, AI-integrity protocol, Claim-Evidence Register, and cross-year sampling rules remain included.

## Research basis

The reference corpus distinguishes:

- official winner and nominee records from the [iGEM Annual Results](https://competition.igem.org/results/);
- observations from individual team wiki pages;
- reusable principles, meaningful exceptions, limitations, and accessibility risks.

Award-winning pages are precedents to analyze, not templates to copy. Historical patterns are not judging rules. Current criteria, eligibility, policies, Standard URLs, and deadlines must be refreshed from official iGEM sources when they affect a decision.

Machine-readable sources live in `corpus/award_records.csv`, `corpus/page_reviews.csv`, `corpus/model_review_metadata.csv`, `corpus/model_modules.csv`, and `corpus/source_manifest.csv`; exact official inputs live in `corpus/snapshots/`. The maintained sample follows `igem-wiki/references/sampling-policy.md`. Use `scripts/import_annual_results.py` for reproducible annual imports, then run `python3 scripts/build_corpus.py`. Use `scripts/query_corpus.py` to select only relevant records. The generated compact reviewed-page indexes, Model page taxonomy, Model module evidence index, and separate full award ledgers are committed so a skill can use them without running code.

For example, select Model precedents by scientific role rather than year alone:

```bash
python3 scripts/query_corpus.py model-modules \
  --model-archetype stochastic --project-decision stopping-policy \
  --evidence-scope validated-with-team-data
```

## Installation

### Project-local

Copy all six directories into the project's `.agents/skills/` directory:

```bash
mkdir -p .agents/skills
cp -R /path/to/igem-wiki-skills/igem-* .agents/skills/
```

Install the full collection when using `igem-wiki`, because the coordinator routes specialized work to its five sibling skills. A single domain skill can be installed alone when only that domain is needed.

### Personal

```bash
mkdir -p "$CODEX_HOME/skills"
cp -R /path/to/igem-wiki-skills/igem-* "$CODEX_HOME/skills/"
```

Restart or reload Codex if the new skills are not discovered immediately.

## Usage examples

Every skill begins substantial work with a progressive input preflight. It first inspects the conversation and accessible workspace, then reports what it found, only the minimum missing information, optional inputs that would improve confidence, and the evidence or assumptions it will use to start. A complete request proceeds immediately rather than receiving a generic questionnaire.

For the strongest first pass, include four short items when they are not already visible:

- **Outcome:** research, plan, write, implement, or audit—and what decision the result should support.
- **Target:** wiki root, exact page, repository, document, or URL.
- **Scope:** read-only versus edits, pages allowed to change, language, deadline, and design constraints.
- **Evidence:** relevant code, data, figures, protocols, records, references, and known limitations.

This is a helpful prompt shape, not a mandatory form:

```text
Use $igem-model-wiki.
Outcome: audit Model 3 and propose improvements; do not edit files.
Target: /path/to/wiki/drylab-model.html
Evidence: /path/to/model-code and /path/to/results
Constraint: keep the current visual system and distinguish illustrative runs from validation.
```

```text
Use $igem-wiki to build a Claim-Evidence Register and audit our full wiki against current judging requirements.

Use $igem-model-wiki to review whether a single-sequence demonstration has been generalized beyond its evidence.

Use $igem-hp-wiki to turn our engagement records into an evidence-backed integration log.

Use $igem-wetlab-wiki to review whether our Results figures support their claims and document a complete DBTL cycle.
```

## Templates

- `igem-wiki/assets/templates/whole-wiki-evidence-map.md`
- `igem-wiki/assets/templates/page-brief.md`
- `igem-wiki/assets/templates/figure-evidence-card.md`
- `igem-wiki/assets/templates/team-intake.md`
- `igem-wiki/assets/templates/judging-readiness-matrix.md`
- `igem-wiki/assets/templates/wiki-production-board.md`
- `igem-wiki/assets/templates/browser-qa-report.md`
- `igem-wetlab-wiki/assets/templates/dbtl-cycle.md`
- `igem-model-wiki/assets/templates/model-card.md`
- `igem-hp-wiki/assets/templates/integration-log.md`
- `igem-implementation-wiki/assets/templates/readiness-matrix.md`

## Validation

Run the dependency-free repository validator:

```bash
python3 scripts/build_corpus.py --check
python3 scripts/validate_version.py
python3 scripts/validate_evals.py
python3 -m unittest discover -s tests
python3 scripts/validate_repository.py
```

For a read-only first pass over static HTML:

```bash
python3 igem-wiki/scripts/audit_static_wiki.py /path/to/wiki --no-fail
```

Pass current-season Standard URLs explicitly when needed, for example:

```bash
python3 igem-wiki/scripts/audit_static_wiki.py /path/to/wiki --no-fail \
  --required-route model --required-route human-practices
```

For a shareable report or an explicitly requested network-assisted pass:

```bash
python3 igem-wiki/scripts/audit_static_wiki.py /path/to/wiki \
  --exclude drafts --markdown
python3 igem-wiki/scripts/audit_static_wiki.py /path/to/wiki \
  --check-external --external-timeout 8 --no-fail
```

External checking is optional and allowlisted; keep it out of deterministic CI and interpret connection failures as review prompts.

The checks validate corpus schema and raw-source hashes, duplicate records, official award relationships, domain-year sampling floors, winner/nominee and competition-class coverage, generated-index freshness, release metadata, evaluation contracts, deterministic tool behavior, skill entrypoints, UI metadata, installed-layout references, required resources, and unfinished placeholders. GitHub Actions runs these checks on pushes and pull requests. Behavioral scenarios live in `evals/scenarios.md`; CI checks their structure but does not claim to run a model. See [RELEASING.md](RELEASING.md) for the version and release policy.

## Scope and attribution

This is an independent community resource and is not affiliated with or endorsed by the iGEM Foundation. Team names and links are included for research attribution. The repository summarizes public examples without copying their branding or scientific assets. Recheck official award status before reuse.

## License and citation

Released under the MIT License. See [LICENSE](LICENSE). Citation metadata is provided in [CITATION.cff](CITATION.cff).

---

## 中文简介

这是一组模块化的 iGEM Wiki Codex skills。`igem-wiki` 负责全站证据、赛季合规与跨页面协调，其余五个 skill 分别处理项目叙事、湿实验、建模、Human Practices 和落地实施。v0.9.0 为六个 skill 增加渐进式输入预检：先识别已有材料，只提示真正缺少的信息，并在请求完整时直接开始；同时保留 v0.8.0 的 1,054 条官方奖项记录、101 条页面审阅与覆盖 2021–2025 全区间的 34 条 Model 模块证据记录。
