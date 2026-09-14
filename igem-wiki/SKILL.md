---
name: igem-wiki
description: Plan, write, implement, or audit an entire iGEM team wiki by coordinating project story, wet-lab evidence, modeling, Human Practices, implementation, and site-wide usability. Use for whole-wiki architecture, cross-page consistency, judging readiness, or work spanning multiple iGEM wiki sections; use a domain subskill for a single specialized section.
---

# iGEM Wiki

Build one coherent, evidence-traceable project record. Treat award-winning wikis as precedents to analyze, not visual templates to copy.

## Run the input preflight

At the beginning of a substantial request, inspect the conversation and accessible workspace before asking the user for anything. Then give a short, user-visible readiness note using only the lines that add value:

- **Found:** relevant pages, repositories, evidence, season, and constraints already available.
- **Minimum missing:** only information without which the requested outcome or edit scope would materially change.
- **Optional boost:** inputs that would improve confidence, specificity, or verification but are not required to start.
- **Starting with:** the evidence and assumptions that will be used now.

The usual minimum is the intended mode or outcome, the target page or wiki root when it cannot be discovered, and whether the request is read-only or authorizes edits when that is ambiguous. Judging-readiness work also needs the competition year and team context. Whole-wiki planning benefits from the project statement, current maturity, target medal or awards, strongest evidence, freeze timeline, and pages or design elements that must not change.

Do not make the user complete a long questionnaire before useful work begins. Never ask them to re-provide files or facts that can be inspected. Ask at most a few focused questions when an answer is genuinely blocking; otherwise proceed with explicit assumptions, label missing evidence, and explain how the optional inputs would improve the next iteration. Skip the formal preflight for a small self-contained request.

## Confirm the delivery contract

Before long-running or mutating work, state a compact user-visible contract with the **deliverable**, authorized **scope**, and observable **done when** condition. For file edits or costly runs, put it in the first progress update before the first mutation; for read-only work, it may be folded into the readiness note. Infer these details from the request and inspected workspace; do not ask the user to reconfirm what is already explicit. If a non-blocking detail is uncertain, state the assumption and begin. Update only the affected part when the user changes direction. Skip this contract for a small self-contained request.

## Resume interrupted work

When the user says continue or resume, inspect the current conversation, live files, repository status, generated artifacts, and any available checkpoint before asking for context. Treat a checkpoint as a possibly stale handoff hint: verify it against live state, preserve user changes, and continue from the next exact safe action without repeating completed work or broadening the authorized scope. Ask only when live evidence materially conflicts or required authority is missing.

Create or update a persistent checkpoint only when the user requests or authorizes one. Use [assets/templates/resume-checkpoint.md](assets/templates/resume-checkpoint.md), store it at a user-approved project path, and keep it concise and free of secrets, credentials, identifiable interview data, and private raw records.

## Route the task

Load only the domain instructions needed for the request:

- **Home, Description, Awards, information architecture, navigation, or visual language:** read `../igem-wiki-story/SKILL.md`.
- **Design, Experiments, Engineering, Results, Measurement, Parts, Protocols, or Notebook:** read `../igem-wetlab-wiki/SKILL.md`.
- **Model, dry-lab analysis, equations, computational figures, or reproducibility:** read `../igem-model-wiki/SKILL.md`.
- **Human Practices, Education, Inclusivity, Sustainability, or stakeholder integration:** read `../igem-hp-wiki/SKILL.md`.
- **Implementation, Safety, Entrepreneurship, Hardware, Software, or Contribution:** read `../igem-implementation-wiki/SKILL.md`.

For the current Alternative Platform category, route biological-platform characterization to Wet Lab, deployment and safety evidence to Implementation, and whole-project framing to Story. Historical Results do not contain a same-name 2021–2025 award family, so use current official criteria rather than inventing a legacy mapping. Presentation production is outside this skill collection; the wiki should keep presentation claims consistent and traceable without treating Best Presentation as a wiki-page precedent.

For a whole-site plan or audit, read [references/current-judging.md](references/current-judging.md), [references/cross-page-contract.md](references/cross-page-contract.md), and [references/review-checklist.md](references/review-checklist.md). Read [references/claim-evidence-register.md](references/claim-evidence-register.md) when claims span pages or risk overgeneralization. Read [references/ai-integrity.md](references/ai-integrity.md) whenever AI materially assists submitted work. For precedent research, also read [references/corpus-index.md](references/corpus-index.md) and [references/sampling-policy.md](references/sampling-policy.md).

When the 2026 Competition is in scope, read [references/seasons/2026-judging.md](references/seasons/2026-judging.md) and verify unstable requirements live. Do not silently apply a 2026 snapshot to another season.

## Choose the mode

- **Research:** verify official awards and current judging guidance, then extract recurring decisions from several contrasting wikis.
- **Plan:** inspect the team's live files and evidence, then propose page ownership, cross-links, and priorities without editing.
- **Write:** draft evidence-bounded content using the domain skill and the site's established voice.
- **Implement:** change only the requested scope, preserve unrelated work, and verify the rendered site.
- **Audit:** attach every finding to a page, source, or browser observation and prioritize trust before polish.

## Establish the evidence map

Before substantial writing or restructuring:

1. Inspect the live wiki, repositories, notebooks, datasets, figures, protocols, Registry entries, forms, and citations. Do not assume paths or current asset versions.
2. List the project's main claims. For each claim, record its evidence, status, owner page, supporting pages, limitations, and next decision.
3. Label statements as observed, experimentally measured, computed, literature-derived, stakeholder-reported, proposed, or future work.
4. Keep one canonical owner for each detailed result. Other pages should summarize and link rather than copy divergent versions.
5. If evidence is missing, weaken the claim or mark the gap. Never invent results, iterations, stakeholder influence, validation, citations, or award eligibility.

For a reusable planning artifact, adapt [assets/templates/whole-wiki-evidence-map.md](assets/templates/whole-wiki-evidence-map.md). For a new or substantially revised page, adapt [assets/templates/page-brief.md](assets/templates/page-brief.md). For an important figure, adapt [assets/templates/figure-evidence-card.md](assets/templates/figure-evidence-card.md). At project start use [assets/templates/team-intake.md](assets/templates/team-intake.md); during production use [assets/templates/wiki-production-board.md](assets/templates/wiki-production-board.md); before judging use [assets/templates/judging-readiness-matrix.md](assets/templates/judging-readiness-matrix.md) and [assets/templates/browser-qa-report.md](assets/templates/browser-qa-report.md).

## Build a judge-readable project path

The whole wiki should support this path without forcing it into identical page layouts:

`problem → users and context → proposed system → design choices → build/test evidence → model or measurement insight → iteration → responsible implementation → reusable contribution`

The Home page orients. Description defines the problem and solution. Technical pages prove what was attempted and learned. Human Practices shows how outside perspectives changed the work. Implementation and Safety bound real-world use. Contribution and Attributions preserve what others can reuse and who did the work.

## Check cross-page consistency

- Project name, problem, intended users, biological mechanism, success criteria, and maturity level agree everywhere.
- Description promises only evidence that Results, Model, Measurement, Hardware, or Software can support.
- Engineering links each design change to a test or reason; Results links back to the relevant method and forward to the conclusion.
- Human Practices records concrete changes and unresolved tensions, not merely meetings.
- Implementation, Safety, Sustainability, and Entrepreneurship use compatible assumptions about scale, users, regulation, containment, cost, and readiness.
- Awards or medal summaries point to evidence pages and never replace them.

For a static HTML tree, `scripts/audit_claim_consistency.py PATH --no-fail` can identify candidate number mismatches, maturity-language conflicts, and headline metrics that lack a matching non-summary owner. Use `--exclude RELATIVE_PATH` for drafts and `--markdown` for a shareable review. This is a lexical first pass: every candidate requires checking conditions, units, evidence provenance, and the intended canonical owner before any edit. No finding proves correctness, contradiction, or scientific validity.

## Refresh unstable facts

When judging criteria, competition rules, deadlines, standard URLs, or award status matter, verify the current official iGEM Competition site. Record year, section, prize, winner versus nominee, team, and exact URL. Do not present historical patterns as current rules.

## Match the competition phase

- **Early season:** define users, success criteria, evidence ownership, attribution capture, data provenance, and selected award hypotheses before pages become urgent.
- **Mid season:** audit experiments, modeling, Human Practices integration, Registry work, software or hardware artifacts, and negative results while another iteration is still possible.
- **Pre-freeze:** verify Standard URLs, Judging Form claims, Attributions, Registry and repository links, AI disclosures, external assets, browser behavior, and current deadlines.
- **Post-Jamboree:** add awards and final amendments without rewriting the historical record or erasing limitations.

## Verify implementation

For edits, check syntax and references, then render the real pages at desktop and mobile widths. For a static HTML tree, `scripts/audit_static_wiki.py PATH --no-fail` can provide a read-only first pass for local links and assets, fragments, duplicate identifiers, machine-local paths, image alternatives, figure captions, language, titles, heading count, and heading-level jumps. Repeat `--required-route ROUTE` for current-season Standard URLs, and use `--exclude RELATIVE_PATH` for known non-deployable drafts. Use `--markdown` for a shareable report. Run the allowlisted `--check-external` pass only when network verification is requested; do not make it a deterministic CI gate. Treat warnings as review prompts and do not use this check as a substitute for browser or assistive-technology QA. Test global navigation, local table of contents, anchors, collapsed content, figures, equations, tables, media fallbacks, and outbound evidence links. Essential meaning must remain available without hover, animation, or a particular browser.

## Close the work loop

At handoff, report only the useful parts of: **Delivered**, **Not completed**, **Evidence limits**, **Verification**, and **Best next input or action**. Omit empty fields. Distinguish an artifact being finished from its scientific claims being validated, and never call work complete when a required check failed or was not run. When another iteration depends on the user, name the exact missing item and how it would change the result; otherwise stop cleanly without a generic request for more work.
