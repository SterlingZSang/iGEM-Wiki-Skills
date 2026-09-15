# Evaluation tiers

This repository separates deterministic program tests from model-behavior evaluation.

## Automated in CI

- corpus schema, provenance, coverage, and generated-output checks;
- release metadata consistency;
- behavioral-scenario contract structure;
- unit tests for importer failure conditions and static-audit scope boundaries;
- installer preview, backup, rollback, selection, and doctor security boundaries;
- skill manifests, frontmatter, resources, links, and full or standalone installed-layout checks.

## Behavioral forward tests

`scenarios.md` defines prompts and observable invariants for running the skills with a capable Codex model in an isolated task. The dependency-free CI validates that these contracts remain complete, but it does **not** claim to run or score a model. Before a release that materially changes routing, evidence rules, or permissions, run the affected scenarios independently and record the model, date, result, and any corrective change in the release notes.

Committed forward-test reports live in [`runs/`](runs/). Each report should preserve the tested skill and request shape, model and date when available, observable result, side-effect boundary, corrective change, and residual limitation without presenting a small qualitative sample as statistical proof.
