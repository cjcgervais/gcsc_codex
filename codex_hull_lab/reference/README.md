# Reference Geometry

This folder contains namespaced wrappers over the canonical v5.3
`Inheritable_Dimensions` OpenSCAD files.

- `hull_v5_3_reference.scad`
- `frame_v5_3_reference.scad`
- `slot_plug_reference.scad`
- `anchor_reference.scad`

The wrappers intentionally use `use <...>` so top-level render calls in the
original files do not execute when imported into tests or tooling.
