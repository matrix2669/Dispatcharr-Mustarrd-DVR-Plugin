# Branches

This ledger records why every current branch exists. GitHub remains authoritative for live refs, commits, pull requests, and checks.

Before deleting a branch, transfer user-visible results to `CHANGELOG.md` and durable rationale to `DECISIONS.md`, then remove its entry here.

## Branch index

| Branch | Type | Status | Base | Target | Purpose |
|---|---|---|---|---|---|
| `main` | long-lived | active | repository history | stable source | Approved source baseline; production publication still requires every documented release and dependency gate. |
| `dev` | long-lived | active | `main` | `main` | Integrate and validate the next plugin version; approved independent-padding beta 0.3.0-beta.1 is integrated. |
| `fix/zero-handoff-disabled` | fix | integrated; retained | `dev` at `bff2963` | `dev` | Disable automatic Dispatcharr removal at zero minutes; publish approved beta.3. |
| `feature/workspace-standards-reconciliation` | work | active; validated | `dev` at `606d2c2` | `dev` | Add mandatory workspace standards drift and reconciliation guidance. |

## Active records

### `main`

- Current source version: `0.2.13-beta.2`; `v0.2.13-beta.2` identifies this dependency-audit test build, while `v0.2.13-beta.1` remains immutable at its original tested commit.
- Purpose: approved source baseline. No GitHub Releases currently exist, and `TODO.md` keeps production publication blocked until dependency readiness is proven.
- Integrated on 2026-08-22: repository rename/logo workflow, complete available-history documentation, dependency ledger, production-readiness TODO, and dual Mustarrd structured-EPG field compatibility.

### `dev`

- Purpose: integrate the next version under the standalone workflow.
- Current plugin version: `0.3.0-beta.1`; immutable tag resolves to `b91e6b4729d2620b7d14355a049e0bf8be1d5910`. Previous `v0.2.13-beta.3` remains immutable.
- Current state: independent-padding beta fast-forward integrated on 2026-10-21; publication evidence below. Production dependency gates remain open.
- Preserved identity: display name `Mustarrd DVR Handoff`, slug/source directory `mustarrd-dvr-handoff`, configuration, scheduler state, and runtime behavior.
- Validation: all 34 unit tests pass; compilation, JSON and version agreement pass. Exact beta source CI on owning branch/dev/tag passes (runs `39523081671`, `39523140136`, `39523141740`). Published beta archive passes disposable official Dispatcharr 0.31.0 and 0.32.0 installation/overwrite/loading and 16 installed-package regressions per version. Independent exact-release review reports no blockers.
- Deployment validation: `0.2.13-beta.1` was published through the renamed repository and development registry; the user confirmed the installation and resized logo work correctly in Dispatcharr.

## Historical branch conversion

All 14 branches from `v0.1.0` through `v0.2.12` were converted to annotated tags at their exact commits and deleted from GitHub on 2026-08-22. Their release history remains in `CHANGELOG.md`; the deleted branches are intentionally absent from the live branch index.

### `feature/workspace-standards-reconciliation`

- Purpose: record and enforce the mandatory workspace standards drift and reconciliation check before substantive project work.
- Base: `dev` at `606d2c2`.
- Intended target: `dev`.
- Scope: `AGENT.md`, `WORKSPACE-STANDARDS.yaml`, and this branch ledger record only.
- Exclusions: no plugin runtime, dependency contract, version, release, registry, scheduler, handoff, or safety behavior changes.
- Validation: workspace standards validation and `git diff --check` pass; no code or test behavior changed.
- Started: `2026-08-24`.

### `fix/zero-handoff-disabled`

- Base: fresh `origin/dev` at `bff2963`; target: `dev` after authorized testing/integration.
- Scope: allow zero `handoff_minutes` to preserve Dispatcharr schedules while mirroring; tests, help text, README, changelog, decision capture, standards reconciliation.
- Approved on 2026-10-09: integrate this scoped beta into source `dev`, publish immutable `v0.2.13-beta.3`, and update registry `dev`. Stable `main`, GitHub Release, live Dispatcharr operations, force pushes, and branch deletion remain excluded.
- Validation: 23 unit tests pass; plugin Python compilation, JSON parsing, version agreement at unchanged 0.2.13-beta.2, existing tagged archive layout, standards reconciliation, and `git diff --check` pass. Independent review completed without blocking findings.
- Original local checkpoint: `d0857c1`. Beta preparation passes all 23 unit tests and disposable official Dispatcharr 0.31.0 installation, beta.2-to-beta.3 overwrite, loader discovery, default merging and installed-package regressions. Added CI checks the exact source commit and archive; publication waits for its green run. Dependency production gates remain open; live installation is not authorized.

- Beta.3 publication evidence: source/dev/tag `c5adaf5215daba6ea7211c9a5257b4f2beb8237f`, tag object `8b5727062277f976b647d3940151369103e8f99e`, source/dev/tag CI green. Archive runtime matches tag byte for byte; SHA-256 `90899f25f6696f07ed895f845bc1e4dc3163407b1990dbe66dac6e9323b6bbf5`. Registry publication follows its own reviewed metadata change. Work branch is retained; live installation remains pending user action.

### `feature/independent-recording-padding`

- Base: dev `c46f246c4c2a219c9d72ca7309a15c1777aa35fc`; target dev.
- Implementation checkpoint: `1d2f371d29decffddf0d07e790fe9078d47c53d9`.
- Approved next-beta scope: prepare 0.3.0-beta.1, reconcile standards, publish
  owning source/dev/tag and testing registry dev. Stable main, GitHub Release,
  live installation, Mustarrd changes and recording operations remain excluded.
- No source dev-test branch is prescribed; testing registry uses dev after the
  established migration. Keep existing source main and all prior tags intact.
- Original 34 source tests and 16 installed-package tests passed; independent
  review fixed an oversized-integer edge and re-review found no blockers.
- Release candidate requires exact-commit CI, independent review and disposable
  official 0.31.0/0.32.0 install/old-beta overwrite/default merging/regressions.
  Record completed publication evidence in the workspace checkpoint.
- Governance: reviewed central lifecycle/approval/exact-SHA policy changes and
  aligned AGENT.md; reconcile the applied baseline for this promotion boundary.

- Beta publication completed: source owning/dev/tag accepted commit
  `b91e6b4729d2620b7d14355a049e0bf8be1d5910`, immutable `v0.3.0-beta.1` tag object
  `98a5baaf6cfcc0768e35ea5ef2682bed87eb19c0`. Exact-source CI runs `39523081671`,
  `39523140136`, `39523141740` pass both pinned official Dispatcharr versions.
- Archive SHA-256 `6ef378d2d5dfc5858fa322e42e5cf9d44ebe82adb3394bd305d128520212261f`
  byte-matches the release runtime and passed official 0.31.0/0.32.0 clean install,
  prior-beta overwrite, loader/default merging and 16 installed-package tests each.
  All 34 source tests pass; independent release review reports no blockers.
- Registry dev `49f063478d5ba030bf3cd63e1c78f3728e44cbb8` advertises this exact beta.
  Registry CI `39523294261`, seven tests, validator, independent review and public
  raw root/detail/archive readback pass. Prior history and unrelated entries are
  preserved. Post-publication source documentation checkpoint may advance dev
  without moving the immutable release tag. No runtime change in that checkpoint.
- Installation and live validation remain pending; no live recordings, Mustarrd
  changes, restarts, stable main or GitHub Release operations occurred.
