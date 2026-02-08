#!/usr/bin/env bash
set -euo pipefail

PRESET="${1:-gcsc_default}"
OUT_NAME="${2:-gcsc_hull.stl}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PRESET_FILE="$LAB_ROOT/presets/${PRESET}.scad"

if [[ ! -f "$PRESET_FILE" ]]; then
  echo "Preset not found: $PRESET_FILE" >&2
  exit 1
fi

if ! command -v openscad >/dev/null 2>&1; then
  echo "OpenSCAD CLI not found in PATH." >&2
  exit 1
fi

mkdir -p "$LAB_ROOT/exports/stl"
TMP_ENTRY="$LAB_ROOT/_tmp_export_entry.scad"
OUT_PATH="$LAB_ROOT/exports/stl/$OUT_NAME"

cat > "$TMP_ENTRY" <<EOF
include <presets/${PRESET}.scad>
include <src/gcsc_hull_core.scad>

gcsc_hull_build();
EOF

(
  cd "$LAB_ROOT"
  openscad -o "$OUT_PATH" "_tmp_export_entry.scad"
)

rm -f "$TMP_ENTRY"
echo "Exported STL: $OUT_PATH"
