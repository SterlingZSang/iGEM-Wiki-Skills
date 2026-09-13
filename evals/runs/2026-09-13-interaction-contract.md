# Interaction-contract forward test — 2026-09-13

## Run context

- Candidate: working tree after v0.9.0
- Evaluator: primary Codex agent
- Test agents: independent Codex subagents using the session-default model; the exact model identifier was not exposed to the evaluator
- Skills: all six iGEM Wiki entrypoints
- Project evidence: `/Users/travis/PyCharmMiscProject/Wiki`
- Mutation boundary: the project Wiki remained read-only; Story edits used isolated files under `/private/tmp/igem-skill-forward-test/`

The test agents received the skill path and realistic user request, but not the expected invariants or suspected failure.

## Results

| ID | Skill | Request shape | Result | Observable behavior |
|---|---|---|---|---|
| FT-01 | `igem-model-wiki` | vague improvement request with an inspectable workspace | Pass | Located the Model page and artifacts, completed a useful read-only audit, avoided repeated intake questions, and bounded computational versus biological evidence. |
| FT-02 | `igem-model-wiki` | one-sentence caption rewrite | Pass | Answered directly without preflight or closing ceremony and removed the validation overclaim. |
| FT-03 | `igem-wiki-story` | fully specified, single-file implementation | Partial | Respected the file and section boundary and verified desktop/mobile behavior, but did not visibly state the delivery contract before the first edit. |
| FT-04 | `igem-wetlab-wiki` | read-only Results audit with calibration missing | Pass | Proceeded without blocking, treated the page as a provisional template, and named the exact experimental inventory needed for the next iteration. |
| FT-05 | `igem-hp-wiki` | vague request with sparse engagement records | Pass | Inspected available pages and meeting notes, produced a useful architecture, requested only a minimized anonymous record, and did not infer stakeholder integration. |
| FT-06 | `igem-implementation-wiki` | complete read-only deployment-readiness audit | Pass | Started directly, kept the requested scope, distinguished safety statements from verified controls, and did not claim deployment readiness. |
| FT-07 | `igem-wiki` | complete cross-page consistency audit | Pass | Returned five file-grounded contradictions with canonical evidence owners and separate measured, computed, stakeholder-reported, and planned states. |
| FT-08 | `igem-wiki-story` | repeat of FT-03 after correction | Pass | The first progress update stated the deliverable, single-file scope, preserved visual constraint, and desktop/mobile completion condition before editing; the final handoff reported the evidence boundary and verification. |

## Corrective change

FT-03 showed that a correct final scope is not enough when a mutating task begins silently. All six skills now require the delivery contract to appear in the first progress update before any file mutation or costly run. Read-only work may still fold it naturally into the readiness note, and small self-contained requests continue to skip the ceremony.

The retest passed without requiring fixed labels or repeated user confirmation.

## Residual limitations

- These are bounded qualitative forward tests, not statistical model evaluation.
- The exact test-model identifier was unavailable; future published runs should pin and record it when the environment exposes that value.
- The tests measure observable task behavior, not user satisfaction after long-term team use.
