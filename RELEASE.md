# Release Process

## Version and channel rules

- Keep `VERSION`, `mustarrd-dvr-handoff/plugin.json`, `Plugin.version`, `CHANGELOG.md`, and the Git tag synchronized.
- Use `vMAJOR.MINOR.PATCH-beta.N` tags for testing and normal `vMAJOR.MINOR.PATCH` tags for completed work.
- Never create a permanent version branch or move a published tag.
- Publish beta and completed tags through `dispatcharr-plugins:dev`.
- Create a GitHub Release and update `dispatcharr-plugins:main` only with explicit user approval.

## Required validation

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile mustarrd-dvr-handoff/*.py
python3 -m json.tool mustarrd-dvr-handoff/plugin.json >/dev/null
```

Run the `Validate plugin` GitHub workflow for the exact source commit before registry publication. Its disposable official Dispatcharr installer/loader harness uses pinned 0.31.0 and 0.32.0 source with framework/database boundaries stubbed and does not replace live end-to-end dependency validation.

Also verify version agreement, the exact tag commit, the archive's `mustarrd-dvr-handoff/` layout, the logo URL, and a Dispatcharr install/update. Recheck the official Dispatcharr plugin contract whenever its supported or deployed version changes.

## Beta publication

Integrate the versioned change into `dev`, tag the tested commit, push the tag without creating a GitHub Release, and update only `dispatcharr-plugins:dev` to the exact tag and commit. Dispatcharr updates are version-driven.

## Stable completion and release

After testing, finalize the stable version, promote the exact code to `main`, tag it, and point the registry `dev` channel to that completed tag. A normal tag does not authorize a Release. When the user explicitly approves a Release, attach a clean ZIP containing only the `mustarrd-dvr-handoff/` plugin directory plus a checksum, then make a focused registry `main` update.

## Independent-padding beta approval

The operator approved the next beta publication on 2026-10-21. Fresh remote refs
showed latest `v0.2.13-beta.3`; this feature uses `0.3.0-beta.1` under Semantic
Versioning. Approval covers the owning source branch, source `dev`, immutable
beta tag and registry `dev`, plus related workspace documentation. This supersedes
the original local-only limit. There is no active source `dev-test` requirement;
the testing registry migrated to `dev` (ADR-013). No GitHub Release is required
for this beta: publish the immutable tag archive. Stable main, live installation,
restarts and recording operations remain excluded.

Validate the exact candidate and prior-beta overwrite in isolated official
Dispatcharr 0.31.0 (`bcbb68c4f054ee56383a41604cfcd7302b85da66`) and 0.32.0
(`c52bf87acb7ff2d787d6dcfb9fe3d39999585912`) installer/loaders, full source tests,
metadata agreement, independent review and source CI before registry publication.
The checks use framework/database stubs and do not establish live compatibility.
Reconcile standards before promotion; verify fresh source/dev/tag/registry heads
and raw root/detail/archive identity after publication. Preserve all prior versions
and unrelated catalog entries. Existing production dependency gates remain open.

Installation remains a separate pending approval. First verify target versions,
preserve settings/scheduler state, keep automatic work disabled until Dry Run is
configured, and inspect blank/zero/one-sided options and mismatch retention in a
disposable dev-test instance. No live recording creation/cancellation is authorized.
