# Release process

Normal commits describe the change; semantic versions belong to release commits, tags, and GitHub Releases.

- Use `fix:` or `feat:` commits while developing.
- Use a patch version for backward-compatible corrections, a minor version for new capabilities or corpus/schema expansion, and a major version for breaking installation or interface changes.
- Create one final `chore(release): vX.Y.Z` commit after all release metadata agrees.
- Tag that exact commit as `vX.Y.Z` and create the matching GitHub Release.

## Release gate

1. Move completed notes from `[Unreleased]` to a dated version section.
2. Update `VERSION`, every skill `manifest.json`, `CITATION.cff`, the README current release and counts, and any version-specific prose.
3. Refresh official source snapshots when the corpus changed.
4. Run:

   ```bash
   python3 scripts/build_corpus.py --check
   python3 scripts/validate_version.py
   python3 scripts/validate_evals.py
   python3 -m unittest discover -s tests
   python3 scripts/validate_repository.py
   python3 scripts/install_skills.py /tmp/igem-wiki-release-test --apply
   python3 igem-wiki/scripts/doctor.py /tmp/igem-wiki-release-test --source .
   ```

5. Run affected behavioral scenarios independently when routing, evidence, or authorization decisions changed; CI only validates their structure.
6. Push the release commit, create and push an annotated tag, publish the GitHub Release, and verify that the tag, Release, `VERSION`, and default branch resolve to the intended commit.
