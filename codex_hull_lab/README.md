# Great_Canadian_Soap_Canoe Lab

This folder is the Codex-first OpenSCAD + BOSL2 lab for the
Great Canadian Soap Canoe hull.

It is an overlay workspace. Canonical governance remains in:

- `00_Governance/`
- `00_Governance_v1-v5_DEPRECATED_REFERENCE/` (reference only)

Canonical v5.3 inheritance source for this lab:

- `codex_hull_lab/Inheritable_Dimensions/`

## Quick Start

1. Open `codex_hull_lab/src/gcsc_hull_entry.scad` in OpenSCAD.
2. Press `F5` for preview or `F6` for render.
3. Switch preset by editing the include in `gcsc_hull_entry.scad` or using `codex_hull_lab/tools/export_stl.ps1`.
4. Export output to `codex_hull_lab/exports/stl/` or `codex_hull_lab/exports/3mf/`.
5. Render a preset preview directly from terminal:
   - `codex_hull_lab/tools/render_preview.ps1 -Preset gcsc_fast_print`
6. Export a 20 mm center slice for flat-cut calibration:
   - `codex_hull_lab/tools/flat_cut_calibration.ps1 -Preset gcsc_default -FlatCutZ -51.2`
7. Run reference compatibility visual check:
   - Open `codex_hull_lab/tests/reference_assembly_check.scad`
   - Confirm frame and plugs align with all four slot interfaces
8. Run authoritative full validation (single source of truth for local + CI):
   - `python codex_hull_lab/tools/validate_full.py --output-json _codex/reports/full_validation_report.json`
9. Confirm slot-mechanism acceptance criteria:
   - `codex_hull_lab/docs/SLOT_MECHANISM_ACCEPTANCE.md`
10. Build release bundle (STL/3MF + provenance + reports):
   - `python codex_hull_lab/tools/package_release.py --version vYYYYMMDD-HHMMSS`
11. Run hygiene maintenance (archive stale `_codex/tmp_*`, normalize inherited docs):
   - `python codex_hull_lab/tools/hygiene_maintenance.py`

Public build module used by entry:

- `gcsc_hull_build()`

## Structure

- `docs/`: spec, parameters, print profile, and iteration notes.
- `features/`: optional overlay feature-pack namespace (non-core).
- `reference/`: wrappers for canonical v5.3 geometry references.
- `src/`: modular hull implementation with one entry point.
- `presets/`: named parameter bundles for fast iteration.
  - `gcsc_mechanics_locked.scad` is the functional baseline.
  - style presets (`gcsc_default`, `gcsc_fast_print`, etc.) override profile controls only.
- `tests/`: render smoke checks and parameter sweep geometry checks.
- `tools/`: local export/render/calibration automation scripts.
- `third_party/BOSL2/`: BOSL2 vendor slot (this repo currently references `02_Production_BOSL2/lib/BOSL2`).

## Governance Notes

- Article 0 constraints still apply (open top, elevated soap support, no hull-floor drain holes in canonical product behavior).
- The drainage feature toggle exists for experiments and is OFF by default.
- Interface geometry to frame/slot systems is locked by `src/gcsc_reference_params.scad`.
- Slot mechanism acceptance and deterministic gate expectations are defined in `docs/SLOT_MECHANISM_ACCEPTANCE.md`.
- Archive non-canonical artifacts under `_codex/` or `docs/archive/`.
