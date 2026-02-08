---
name: render
description: Quick render of a specific .scad file with analysis. Renders the file, reads the image, and reports specific geometric observations.
argument-hint: "<file.scad> [camera: iso|top|side|front|slot_detail|assembly|cross_section]"
allowed-tools: Bash, Read, Glob, mcp__gcsc-openscad__render_file, mcp__gcsc-openscad__list_camera_presets
---

# Quick Render Skill

You are rendering a specific OpenSCAD file and providing geometric analysis.
This is the fast-feedback loop for checking geometry during development.

## Arguments

Parse `$ARGUMENTS` for:
1. **File path** — the .scad file to render (required)
2. **Camera preset** — named preset (optional, default: `iso`)

Examples:
- `/render hull_v6_simple.scad` → renders with iso camera
- `/render modules/hull_simple.scad top` → renders with top-down camera
- `/render assembly_complete.scad assembly` → renders with assembly camera

## Procedure

### Step 1: Resolve File Path

- If path is relative, resolve from `01_Prototype_Simple/`
- If file not found there, try project root
- If still not found, list available .scad files and ask

### Step 2: Render

Use `mcp__gcsc-openscad__render_file` with:
- The resolved file path
- The requested camera preset (or `iso` default)
- Default resolution (1024x768)

### Step 3: Read and Analyze

1. Read the rendered PNG file
2. Describe **3 specific geometric features** visible in the render:
   - Name the feature (e.g., "gunwale edge", "slot opening", "ball pivot")
   - Describe its shape and position
   - Note whether it looks correct
3. List anything that appears **wrong or missing**
4. State confidence: low / medium / high

### Step 4: Report

```
=== RENDER: [filename] ===
Camera: [preset name]
Output: [output path]

OBSERVATIONS:
1. [Feature]: [description]
2. [Feature]: [description]
3. [Feature]: [description]

MISSING/WRONG: [list or "none detected"]
CONFIDENCE: [low/medium/high]
```

## Available Camera Presets

| Preset | Best For |
|--------|----------|
| iso | General overview, overall shape |
| top | Slot openings, symmetry check |
| side | Profile, sheer line, freeboard |
| front | Cross-section, deadrise angle |
| slot_detail | Close-up of slot geometry |
| assembly | Hull + frame together |
| cross_section | Internal geometry, wall thickness |
| frame_detail | Frame structure close-up |
| side_close | Side profile detail |
| alignment | Overall alignment check |

## FORBIDDEN

- Saying "looks good" or "renders correctly" without naming specific features
- Skipping the image read step
- Reporting on geometry you cannot see in the render
