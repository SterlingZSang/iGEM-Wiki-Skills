# v1 installation workflow forward test — 2026-09-15

## Run context

- Candidate: v1.0.0 release working tree
- Evaluator: primary Codex agent
- Test agents: two independent Codex subagents using the session-default model; the exact model identifier was not exposed to the evaluator
- Skills: `igem-wiki` installation and diagnosis workflow
- Fixtures: isolated targets under `/private/tmp/igem-v1-forward/`
- Mutation boundary: one target was strictly read-only; the second authorized replacement of only `igem-model-wiki`, with every sibling treated as out of scope

The test agents received the skill path, trusted checkout, isolated target, and realistic user request, but not the expected invariants or evaluator conclusions.

## Results

| ID | Skill | Request shape | Result | Observable behavior |
|---|---|---|---|---|
| V1-01 | `igem-wiki` | preview a new six-skill installation without changes | Pass | Ran the installer without `--apply`, reported 66 proposed files across six skills, created no target or backup, and clearly stated that nothing changed. |
| V1-02 | `igem-wiki` | update only Model in an installation containing unrelated Wet Lab customization | Pass | Previewed and applied only `igem-model-wiki`, preserved a recoverable backup, removed one obsolete Model file, verified Model against the trusted source, and left all sibling checksums unchanged. |
| V1-03 | doctor | verify the Model directory directly while a sibling differs | Partial | Post-run evaluator verification found that a direct domain path was normalized to its parent and therefore included the unrelated Wet Lab difference in the result. No file was changed, but the requested diagnostic scope was broader than expected. |
| V1-04 | doctor | repeat direct Model verification after correction | Pass | A direct domain path now selects only that domain, reports standalone mode and v1.0.0, matches the trusted source, and ignores unrelated sibling state. Root-level diagnosis still checks the complete collection. |

## Corrective change

The doctor now records a direct domain-directory selection separately from its containing skill root. Direct `igem-model-wiki` diagnosis inspects only Model, while a direct coordinator path or a skills-root path still checks all discovered siblings. A regression test places a modified Wet Lab skill beside Model and confirms that Model-only diagnosis remains healthy.

## Residual limitations

- These are bounded qualitative tests plus deterministic filesystem verification, not a statistical user-satisfaction measure.
- The exact test-model identifier was unavailable.
- Rollback after a simulated mid-update replacement failure is covered by a deterministic unit test rather than a forward-agent task.
- The installer trusts the local checkout supplied by the user; it does not authenticate downloaded source code or contact GitHub.
