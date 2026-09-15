# User-experience workflow forward test — 2026-09-15

## Run context

- Candidate: Unreleased working tree after v0.10.0
- Evaluator: primary Codex agent
- Test agents: three independent Codex subagents using the session-default model; the exact model identifier was not exposed to the evaluator
- Skills: `igem-model-wiki` and the `igem-wiki` coordinator
- Project evidence: the live Model page was read-only; computation and installation fixtures were isolated under `/private/tmp/igem-v011-forward/`
- Mutation boundary: no project Wiki or installed skill was changed; the compute agent could run a bounded smoke test and, after triage, the requested local fixture

The agents received the skill path and a realistic user request, but not the expected invariants or the evaluator's prior conclusions.

## Results

| ID | Skill | Request shape | Result | Observable behavior |
|---|---|---|---|---|
| UX-01 | `igem-model-wiki` | explain the current Model 3 in Chinese without rewriting | Pass | Explained A–E at a new team member's level, defined symbols and terms, separated current computation from biological validation, identified the single-case boundary, and did not edit the Wiki. |
| UX-02 | `igem-model-wiki` | assess a 10,000 × 100 stochastic sweep before choosing local or HPC | Pass | Inspected the actual entry point, used a 1% smoke test, disclosed measured extrapolation, estimated runtime and resource behavior, selected local execution, and recorded runtime, environment, seed, output scope, and scientific limitations. The full fixture took 82.4 seconds after an approximately 80-second estimate. |
| UX-03 | `igem-wiki` | diagnose an installation containing only `igem-model-wiki` | Pass | Used the doctor read-only, recognized the domain skill as a supported standalone installation, checked files, links, and source freshness, and explained that siblings are required only when the coordinator is installed. |

## Corrective change

No corrective change was required after these three runs. The compute run reinforced an intended distinction: a full run may proceed after triage when the user requested it and the measured estimate shows it is bounded; the skill must still separate computational completion from scientific validity.

## Residual limitations

- These are three bounded qualitative tests, not a statistical measure of reliability or user satisfaction.
- The exact test-model identifier was unavailable.
- The compute fixture is a deterministic workload proxy rather than the team's scientific KMC implementation, so it tests triage behavior rather than biological correctness.
- The installation test covered a healthy standalone Model skill; missing siblings with an installed coordinator remain covered by deterministic unit tests rather than this forward-test sample.
