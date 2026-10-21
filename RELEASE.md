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

Run the `Validate plugin` GitHub workflow for the exact source commit before registry publication. Its disposable official Dispatcharr installer/loader harness uses pinned 0.31.0 source with framework/database boundaries stubbed and does not replace live end-to-end dependency validation.

Also verify version agreement, the exact tag commit, the archive's `mustarrd-dvr-handoff/` layout, the logo URL, and a Dispatcharr install/update. Recheck the official Dispatcharr plugin contract whenever its supported or deployed version changes.

## Beta publication

Integrate the versioned change into `dev`, tag the tested commit, push the tag without creating a GitHub Release, and update only `dispatcharr-plugins:dev` to the exact tag and commit. Dispatcharr updates are version-driven.

## Stable completion and release

After testing, finalize the stable version, promote the exact code to `main`, tag it, and point the registry `dev` channel to that completed tag. A normal tag does not authorize a Release. When the user explicitly approves a Release, attach a clean ZIP containing only the `mustarrd-dvr-handoff/` plugin directory plus a checksum, then make a focused registry `main` update.

## Pending independent-padding development test plan

The local `feature/independent-recording-padding` work is unreleased and retains
version `0.2.13-beta.3` only as the source baseline. Do not install its same-version
archive into a live instance. No source push, integration, tag, registry change or
installation has been approved for this task.

After explicit approval of the stated publication scope:

1. Refresh owning source/dev and workspace refs; preserve concurrent changes.
   Reconcile current standards at the promotion boundary, complete relevant
   dependency checks and confirm review remains applicable to the candidate.
2. Prepare `0.3.0-beta.1` (a feature/minor test version, subject to fresh refs)
   consistently in VERSION, plugin.json, Plugin.version and changelog. Review and
   test that exact commit, including source CI and pinned official disposable
   installation/loader checks. A different commit requires fresh acceptance.
3. Integrate only the approved feature into source `dev`, publish immutable
   `v0.3.0-beta.1` at the accepted exact commit, and update only registry `dev` to
   the verified archive/tag/commit. Verify remote refs and archive metadata.
   Stable `main`, GitHub Release and registry `main` remain excluded.
4. Separately approve installation into a disposable Dispatcharr dev-test
   instance with isolated data. Confirm its exact Dispatcharr/Mustarrd versions
   and compatibility first. Preserve existing plugin settings and scheduler
   state; keep automatic work disabled until dry-run configuration is saved.
   Install/update via that instance's development registry, confirm blank upgrade
   defaults, then test pre/post values, zero and one-sided inheritance with Dry
   Run enabled. Inspect effective padding and existing-schedule mismatch results.
   Do not create/cancel live recordings or restart services.
5. Record exact source/tag/registry/installed versions and evidence before any
   further installation or production approval. The outstanding upstream
   dependency audit remains a production gate.

Local disposable verification (no services/data contacted):

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile mustarrd-dvr-handoff/*.py
python3 -m json.tool mustarrd-dvr-handoff/plugin.json >/dev/null
git archive --format=zip --prefix=source/ HEAD -o /tmp/padding-plugin.zip
python3 scripts/validate_dispatcharr.py /tmp/padding-dispatcharr-official /tmp/padding-plugin.zip
```

The official source directory must contain unmodified Dispatcharr commit
`bcbb68c4f054ee56383a41604cfcd7302b85da66` (0.31.0). This checks installer/loader
and installed-package regressions with framework/database stubs; it is not live
end-to-end acceptance or a claim about the currently deployed host.
