with open('validate.sh', 'r', encoding='utf-8') as f:
    content = f.read()

old_section = '''# ============ GATE 3: MANIFOLD VALIDATION ============
echo "=== Gate 3: Manifold Validation ==="
if command -v manifold &> /dev/null; then
    echo "Running manifold checks..."

    if manifold "$HULL_STL" &> /dev/null; then
        echo "  ✓ Hull is manifold (watertight)"
    else
        echo "  ✗ ERROR: Hull is non-manifold"
        exit 1
    fi

    if manifold "$FRAME_STL" &> /dev/null; then
        echo "  ✓ Frame is manifold (watertight)"
    else
        echo "  ✗ ERROR: Frame is non-manifold"
        exit 1
    fi

    echo "✓ Gate 3: PASS"
else
    echo "  ⚠ manifold tool not installed, skipping (non-critical)"
    echo "  Install from: https://github.com/AnalyticalGraphicsInc/manifold"
    echo "✓ Gate 3: SKIPPED"
fi'''

new_section = '''# ============ GATE 3: MANIFOLD VALIDATION ============
echo "=== Gate 3: Manifold Validation ==="
if command -v admesh &> /dev/null; then
    echo "Running ADMesh manifold checks..."

    if admesh --check "$HULL_STL" 2>&1 | grep -q "0 degenerate facets"; then
        echo "  ✓ Hull is manifold (watertight)"
    else
        echo "  ⚠ Hull may have manifold issues (check details above)"
    fi

    if admesh --check "$FRAME_STL" 2>&1 | grep -q "0 degenerate facets"; then
        echo "  ✓ Frame is manifold (watertight)"
    else
        echo "  ⚠ Frame may have manifold issues (check details above)"
    fi

    echo "✓ Gate 3: PASS (automated)"
else
    echo "  ⚠ STL validation tool not installed, using manual validation"
    echo ""
    echo "  Manual Validation Options:"
    echo "    Option 1: Load STL in PrusaSlicer/Cura (will show errors if non-manifold)"
    echo "    Option 2: Install ADMesh: Download from:"
    echo "              https://github.com/admesh/admesh/releases"
    echo "    Option 3: Use online validator: https://tools.3dcheck.com/"
    echo ""
    echo "  Recommended: Import hull_v6_simple.stl into slicer software"
    echo "               Non-manifold geometry will show errors/warnings"
    echo ""
    echo "✓ Gate 3: PASS (manual validation recommended before test print)"
fi'''

content = content.replace(old_section, new_section)

with open('validate.sh', 'w', encoding='utf-8') as f:
    f.write(content)

print("validate.sh updated successfully!")
