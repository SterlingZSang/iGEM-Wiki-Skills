---
name: igem-model-wiki
description: Research, plan, write, implement, or audit an iGEM Model wiki page using current judging guidance, award-winning precedents, and the team's actual code, data, and experimental evidence. Use for Model-page architecture, scientific narrative, equations, figures, reproducibility, dry-lab/wet-lab integration, or page-level UX; do not use for unrelated wiki sections.
---

# iGEM Model Wiki

Build a Model page that lets a judge trace each important conclusion from biological question to reproducible evidence. Treat award-winning pages as precedents to analyze, not templates to copy.

## Choose the smallest workflow

Answer a small, self-contained modeling or wording question directly. For one model module, inspect only its page, code, data, and relevant guidance. Use the full evidence inventory, reproducibility, and browser workflow only for substantial, mutating, or high-risk work. When the goal is understanding rather than publication, explain in the user's language and at their level, define symbols and terms, distinguish computation from biological evidence, and keep publishable Wiki copy separate. Do not edit files unless requested.

## Run the input preflight

Before substantial work, inspect the conversation and workspace, then briefly tell the user what was found, the minimum missing information, optional inputs that would improve confidence, and what you will use to start. The minimum is normally the target Model page or module, the requested mode or outcome, and the permitted edit scope when ambiguous. Useful modeling inputs include the biological question, decision the model should support, code or notebook entry point, input data, expected outputs and units, parameter provenance, assumptions, calibration or comparison evidence, uncertainty or sensitivity work, figures, reproduction instructions, and wet-lab or design consequences.

Do not ask the user to summarize code or data that can be inspected. If only optional validation evidence is missing, proceed with an evidence-bounded audit or draft and mark the limitation. If the requested conclusion depends on unavailable biological calibration, explain that dependency before promising the deliverable. A complete request should move directly into work rather than receiving a generic checklist.

## Confirm the delivery contract

Before long-running or mutating work, briefly state the intended deliverable, authorized scope, and observable completion condition. For file edits or costly runs, put this contract in the first progress update before the first mutation; for read-only work, it may be folded into the readiness note. Infer the details from the request and model artifacts, do not reconfirm what is explicit, and proceed under a stated assumption when uncertainty is non-blocking. Skip this for a small self-contained request.

## Resume interrupted work

When the user says continue or resume, inspect the current conversation, live Model page, code and data state, repository status, generated figures, and any available checkpoint before asking for context. Treat a checkpoint as a possibly stale hint and verify it against live state. Preserve user changes, do not rerun completed calculations or broaden scope, and continue from the next exact safe action. Ask only when live evidence materially conflicts, reproducibility cannot be established, or required authority is missing. Create a persistent checkpoint only when the user requests or authorizes one; if the coordinator skill is installed, use its resume-checkpoint template, otherwise record the same concise fields without secrets or private data.

## Choose the mode

- **Understand:** explain the model, equations, code, outputs, and evidence boundaries without turning the explanation into a publication claim.
- **Research:** identify relevant Best Model and Best Wiki winners and extract reusable patterns.
- **Plan:** inspect the team's sources and propose a page architecture without editing.
- **Write or implement:** create or revise only the requested Model-page content and assets.
- **Audit:** report evidence, narrative, usability, and reproducibility gaps before proposing changes.

If the user asks to research winners or compare exemplars, first use the compact [module evidence index](references/generated/model-modules.md) to select a comparable biological question, method, evidence scope, validation role, and project decision. Use the page-level [Model taxonomy](references/generated/model-taxonomy.md) when no sufficiently similar module is indexed or when page architecture is the comparison target. Read [references/benchmark-patterns.md](references/benchmark-patterns.md) for reusable principles or [references/benchmark-corpus.md](references/benchmark-corpus.md) for exact reviewed examples; do not load both unless the requested comparison requires them. Then read only the relevant rows in the [reviewed-page index](references/generated/reviewed-pages.md). Read the full [official award ledger](references/generated/award-ledger.md) only when verifying or listing winners and nominees. Verify consequential details live. For planning, writing, implementation, or review, read [references/review-checklist.md](references/review-checklist.md) only when a full page-level check is needed.

Treat the module index as a retrieval aid, not a complete decomposition of every reviewed page. Prefer two or three modules that match the team's actual scientific problem over a large prestige-weighted list. Read each selected module's limitation and parameter provenance before borrowing a presentation pattern.

## Triage computational work

Before a non-trivial run, inspect the actual entry point, input size, parameter grid, replicate count, algorithmic scaling, available hardware, expected outputs, and resumability. Run a small representative smoke test when safe, and label runtime estimates as measured extrapolations or theoretical bounds. Estimate wall time, CPU or GPU needs, peak memory, storage, and parallelism before choosing local execution or HPC; do not launch an expensive full run merely to discover its cost.

Prefer local execution for bounded, reproducible work that fits the available environment. Recommend HPC for large parameter sweeps, many stochastic replicates, memory-heavy structures, long molecular simulations, or jobs that need robust checkpointing or scheduling. When either route is reasonable, explain the tradeoff and let the user's time and access constraints decide. Record software versions, hardware, seeds, commands, wall time, cached intermediates, and restart instructions so the result can be reproduced and resumed.

For a new model module, model handoff, or reproducibility record, adapt [assets/templates/model-card.md](assets/templates/model-card.md). When one sequence or parameter set is only used to demonstrate that a workflow runs, label it an illustrative example and state what additional coverage is needed before generalization.

## Start from current evidence

1. Inspect the live workspace before proposing substantial changes: Model HTML, styles, scripts, figures, model code, notebooks, data, reports, and references. Search first; do not assume paths or asset versions.
2. Build an evidence inventory for each model: biological question, decision it supports, inputs, outputs, assumptions, parameters and units, algorithm or equations, calibration or comparison data, uncertainty, sensitivity, validation, limitations, code/data location, and wet-lab or design consequence.
3. Mark every planned statement as one of: directly observed, computed under declared assumptions, literature-derived, hypothesis, or future work. Weaken or remove claims that outrun the source evidence.
4. If essential scientific sources are missing, state the gap and continue with an evidence-bounded plan. Do not invent equations, parameter values, validation, or experimental impact.

For machine-learning or AI-assisted analysis, also document dataset provenance and license, training/validation/test separation, leakage checks, baselines, metrics, uncertainty, applicability domain, software versions, random seeds, human verification, and current iGEM disclosure obligations.

## Refresh unstable facts

When award status, judging criteria, or competition rules matter, verify them on the current official iGEM Competition site. Start from the official Results page and current Judging pages. Record year, competition class, prize, winner versus nominee, team, and exact page URL. Select precedents by the team's actual modeling need first; use recency and class as secondary filters, then add an older or structurally different example to avoid copying one fashion.

## Build the scientific story

Open with a compact map of the modeling system: the project problem, why modeling is needed, how modules connect, and what decisions or experiments they inform. Make inputs and outputs visible before technical depth.

For each genuinely independent model or method, provide the smallest complete reasoning unit appropriate to the science. Usually include:

1. **Question or purpose** — the biological uncertainty or design decision.
2. **Background and assumptions** — scope, simplifications, boundary conditions, and what the model cannot establish.
3. **Method** — variables, units, governing relationships, algorithm, parameter provenance, and implementation details needed to understand or reproduce it.
4. **Results** — interpretable figures or tables, quantitative takeaways, uncertainty or sensitivity, and comparisons against experiments, literature, baselines, or withheld data where available.
5. **Impact and limits** — what changed in design or wet-lab work, what remains provisional, and the next discriminating test.

Use the project's established module vocabulary when it is clear. Do not force unrelated analyses into one catch-all Method, and do not split one coherent method merely to create more sections. Preserve the distinction between prediction, proxy, annotation, hypothesis, and experimental proof.

## Make evidence inspectable

- Define every symbol near its first use and give units for dimensional quantities.
- Trace parameter values to measurements, literature, fitting, or explicit scenario assumptions.
- Show representative intermediate results when they explain how an output was produced.
- Pair every result figure with a caption that states what is plotted, under which conditions, and what conclusion is supported.
- Include controls or baselines, robustness or sensitivity checks, and failure cases when they materially affect interpretation.
- Link code, data, model artifacts, and references when available. Explain how to reproduce key results at a useful level; do not claim reproducibility from a repository link alone.
- Keep negative, partial, and inconclusive results when they changed the project or define model limits.

## Design for a long technical page

- Provide a readable overview before equations and dense results.
- Use a hierarchical table of contents or position-aware navigation for multiple models and subsections. Hash links must reveal any collapsed parent and land on visible content.
- Use progressive disclosure for long derivations or secondary detail, while keeping assumptions, primary results, and limitations visible.
- Prefer diagrams, plots, tables, and annotated workflows over decorative animation. Never hide scientific meaning in hover-only interactions.
- Keep heading levels semantic, figures accessible, formulas legible, and mobile layouts usable.
- Preserve the site's accepted visual system unless the user requests a redesign. Do not imitate an award winner's branding, illustrations, or code.

## Deliver in verifiable stages

For research or audit work, return:

- a source table distinguishing official award evidence from observations about team pages;
- recurring patterns, meaningful exceptions, and anti-patterns;
- a gap analysis against the team's current Model page;
- a prioritized architecture or revision plan tied to available evidence.

For implementation work, edit only the requested scope, preserve unrelated user changes, and verify in proportion to risk:

1. Check HTML/JS syntax and broken local references.
2. Verify navigation, anchors, collapsed sections, equations, figures, and outbound code/data links.
3. For substantial visual or structural changes, first render one representative model section; continue to the broader pattern unless the preview reveals a material evidence or design conflict.
4. Render the real page in a browser at desktop and mobile widths; inspect the top, representative technical sections, and the end.
5. Re-check scientific claims against the evidence inventory after layout edits.

Do not present award-derived patterns as judging rules. Report both scientific and UX limitations instead of hiding them behind polish.

## Close the work loop

At handoff, report only applicable items: what was delivered, what remains outside scope, evidence or validation limits, verification performed, and the single most useful next input or action. Omit empty fields, distinguish computational completion from biological validation, and do not ask generically for more work.
