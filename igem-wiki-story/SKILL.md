---
name: igem-wiki-story
description: Plan, write, implement, or audit the narrative and information architecture of an iGEM wiki, especially Home, Description, Awards, navigation, page introductions, and cross-page storytelling. Use for project framing and site-level comprehension; use a domain skill for technical evidence or Human Practices content.
---

# iGEM Wiki Story

Make the project understandable before making it impressive. The opening path should tell a judge what problem exists, who experiences it, what the team built, what evidence was obtained, and where to inspect it.

## Run the input preflight

Before substantial work, inspect the conversation and workspace, then briefly tell the user what was found, the minimum missing information, any optional inputs that would improve the result, and what you will use to start. The minimum is normally the target page or site, the desired mode or outcome, and the permitted edit scope when ambiguous. Useful story inputs include the one-sentence project claim, affected users, proposed system, current maturity, strongest supported result, canonical evidence pages, intended reader, language, and visual elements that must remain unchanged.

Do not ask for information already present in the wiki. If only optional context is missing, proceed with stated assumptions. If the user supplies a complete page and a clear read-only or edit instruction, do not delay the work with a generic questionnaire.

## Confirm the delivery contract

Before long-running or mutating work, briefly state the intended deliverable, authorized scope, and observable completion condition. For file edits or costly runs, put this contract in the first progress update before the first mutation; for read-only work, it may be folded into the readiness note. Infer the details from the request and live site, do not reconfirm what is explicit, and proceed under a stated assumption when uncertainty is non-blocking. Skip this for a small self-contained request.

## Resume interrupted work

When the user says continue or resume, inspect the current conversation, live pages, repository status, generated artifacts, and any available checkpoint before asking for context. Treat a checkpoint as a possibly stale hint and verify it against live state. Preserve user changes, do not repeat finished work or broaden scope, and continue from the next exact safe action. Ask only when live evidence materially conflicts or required authority is missing. Create a persistent checkpoint only when the user requests or authorizes one; if the coordinator skill is installed, use its resume-checkpoint template, otherwise record the same concise fields without secrets or private records.

For precedent research or substantial story work, read the curated findings in [references/benchmark-corpus.md](references/benchmark-corpus.md) and the compact [reviewed-page index](references/generated/reviewed-pages.md). Read the full [official award ledger](references/generated/award-ledger.md) only when verifying or listing winners and nominees. Verify consequential details live.

For a new or substantially restructured page, adapt the coordinator's page-brief template before writing. Preserve the evidence status and maturity from the Claim-Evidence Register in headlines, summaries, and award pages.

## Build the narrative spine

1. Define the problem, affected users, context, and why existing approaches are insufficient.
2. State the proposed synthetic-biology system without overstating maturity.
3. Name the team's strongest measured or computed result and its condition.
4. Show how Design, Engineering, Results, Model, Human Practices, Safety, and Implementation connect.
5. Give each major claim one canonical destination page.

## Assign page roles

- **Home:** a concise orientation and evidence-aware invitation into the project.
- **Description:** the complete problem-to-solution logic, system boundary, users, mechanism, goals, and success criteria.
- **Awards or Judging:** an index mapping claims to the evidence pages; never the only location of evidence.
- **Navigation and page introductions:** explain what a reader will learn and why it matters.

Use progressive detail: one-sentence project statement, short story, system diagram, key evidence, then routes to depth. Preserve essential text when animation, video, counters, or WebGL does not load.

## Audit claims and experience

- Replace global claims with sourced, bounded statements.
- Label prototypes, proposals, simulations, and validated results accurately.
- Check that project name, users, mechanism, numbers, and readiness agree throughout the site.
- Prefer descriptive menu labels and page subtitles over clever but ambiguous names.
- Test the first screen, global navigation, no-motion or reduced-motion path, mobile layout, keyboard path, and link destinations in a real browser.

Do not copy another team's visual identity, mascots, animations, or prose. Extract information-design decisions and adapt them to the team's evidence and established design system.

## Close the work loop

At handoff, report only applicable items: what was delivered, what remains outside scope, evidence or narrative limits, verification performed, and the single most useful next input or action. Omit empty fields, distinguish page completion from scientific validation, and do not ask generically for more work.
