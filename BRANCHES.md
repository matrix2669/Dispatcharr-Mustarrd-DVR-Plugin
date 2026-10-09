# Branches

This ledger records why every current branch exists. GitHub remains authoritative for live refs, commits, pull requests, and checks.

Before deleting a branch, transfer user-visible results to `CHANGELOG.md` and durable rationale to `DECISIONS.md`, then remove its entry here.

## Branch index

| Branch | Type | Status | Base | Target | Purpose |
|---|---|---|---|---|---|
| `main` | long-lived | active | repository history | stable source | Approved source baseline; production publication still requires every documented release and dependency gate. |
| `dev` | long-lived | active | `main` | `main` | Integrate and validate the next plugin version; synchronized for the `0.2.13-beta.2` dependency-audit build. |
| `feature/workspace-standards-reconciliation` | work | active; validated | `dev` at `606d2c2` | `dev` | Add mandatory workspace standards drift and reconciliation guidance. |

## Active records

### `main`

- Current source version: `0.2.13-beta.2`; `v0.2.13-beta.2` identifies this dependency-audit test build, while `v0.2.13-beta.1` remains immutable at its original tested commit.
- Purpose: approved source baseline. No GitHub Releases currently exist, and `TODO.md` keeps production publication blocked until dependency readiness is proven.
- Integrated on 2026-08-22: repository rename/logo workflow, complete available-history documentation, dependency ledger, production-readiness TODO, and dual Mustarrd structured-EPG field compatibility.

### `dev`

- Purpose: integrate the next version under the standalone workflow.
- Current plugin version: `0.2.13-beta.2`.
- Current state: repository-only rename metadata, crop-safe logo, and tag-based workflow are integrated for development publication.
- Preserved identity: display name `Mustarrd DVR Handoff`, slug/source directory `mustarrd-dvr-handoff`, configuration, scheduler state, and runtime behavior.
- Validation: 18 unit tests pass, including upstream- and fork-shaped Mustarrd payloads; all plugin modules compile; JSON and version agreement pass; the logo is a 1254×1254 PNG; 14 historical tag mappings were verified before their version branches were deleted.
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
- Exclusions: publication, promotion, versions, tags, registry manifests, live Dispatcharr operations.
- Validation: 23 unit tests pass; plugin Python compilation, JSON parsing, version agreement at unchanged 0.2.13-beta.2, existing tagged archive layout, standards reconciliation, and `git diff --check` pass. Independent review completed without blocking findings.
- Local-only checkpoint requested on 2026-10-09. Next step: authorized disposable development testing before integration or release; dependency production gates remain open.
