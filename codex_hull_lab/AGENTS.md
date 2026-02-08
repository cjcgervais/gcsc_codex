# Codex Hull Lab Local Manual

Scope: `codex_hull_lab/`

This file is subordinate to root `AGENTS.md`.
If there is any conflict, root `AGENTS.md` and `00_Governance/*` win.

## Working Rules

- Keep geometry edits inside `src/` and parameter edits inside `presets/`.
- Keep generated artifacts in `exports/`.
- Keep design rationale in `docs/ITERATION_LOG.md`.
- Do not edit canonical governance files from this folder.

## Module Ownership

- `src/gcsc_hull_entry.scad`: single user entry point.
- `src/gcsc_hull_core.scad`: top-level hull composition.
- `src/gcsc_hull_profiles.scad`: section and curvature functions.
- `src/gcsc_hull_shell.scad`: shell generation and cut helpers.
- `src/gcsc_hull_features.scad`: keel, rim, and optional feature toggles.
- `src/gcsc_hull_bosl2_adapter.scad`: BOSL2 include/adapter boundary.

## Validation Loop

1. Run `tests/render_test.scad` after source changes.
2. Run `tests/parameter_sweep.scad` after profile changes.
3. Export with `tools/export_stl.ps1` or `tools/export_stl.sh`.
4. Record non-trivial outcomes in `docs/ITERATION_LOG.md`.

Public build call contract:

- `gcsc_hull_build();`
