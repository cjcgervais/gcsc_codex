# Print Profile - A1 Mini Baseline

Last updated: 2026-02-07

## Orientation

- Use the flat-base option when possible (`enable_flat_cut = true`).
- Place hull flat-side down on the build plate.
- Keep open-top direction upward.

## Starting Slicer Profile

- Layer height: `0.16..0.24 mm`
- Nozzle: `0.4 mm`
- Wall loops: `3..4`
- Top layers: `4..6`
- Bottom layers: `4..6`
- Infill: `10..18%` gyroid (or equivalent)
- Supports: off for default open-top orientation; enable only if experimenting with aggressive rocker/overhangs

## Material Baseline

- PLA for early geometry validation.
- PETG after shape lock if bathroom humidity resistance is needed.

## Wall Guidance

- Keep `wall_mm` in the `2.0..2.8` range for reliable shell slicing on a `0.4 mm` nozzle.

## Iteration Mode

- Use `gcsc_fast_print.scad` for short-cycle print checks.
- Use `gcsc_high_stability.scad` for handling and strength checks.
