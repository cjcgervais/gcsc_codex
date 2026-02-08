#!/usr/bin/env bash
# GCSC2 Dual-AI Visual Verification Gate
# Constitution Article IV.6 - MANDATORY BEFORE PHASE APPROVAL
#
# This script implements the dual-AI verification protocol that prevents
# geometry errors by requiring independent verification from both Claude
# and Gemini AI models before accepting a design change.
#
# Authority: GCSC2_Constitution.md v2.0.0, Article IV.6
#            claude.md - Dual-AI Visual Verification Protocol

set -e

echo "============================================"
echo "GCSC2 VISUAL VERIFICATION GATE (Article IV.6)"
echo "============================================"
echo ""
echo "This verification is MANDATORY before Phase 1 freeze."
echo "Both Claude and Gemini must independently verify geometry."
echo ""

# Source .env from GCSC2 root
if [ ! -f "../../.env" ]; then
    echo "ERROR: Cannot find ../../.env"
    echo "Create .env in GCSC2 root with: GEMINI_API_KEY=your_key_here"
    exit 1
fi

source ../../.env || {
    echo "ERROR: Cannot load ../../.env (GEMINI_API_KEY required)"
    exit 1
}

if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY not set in .env"
    exit 1
fi

echo "✓ Environment loaded (GEMINI_API_KEY found)"
echo ""

# Verify renders exist
RENDERS_DIR="renders"
REQUIRED_RENDERS=(
    "hull_v6_simple.png"
    "frame_v6_simple.png"
    "assembly_v6_simple.png"
)

echo "Step 1: Checking required renders..."
for render in "${REQUIRED_RENDERS[@]}"; do
    if [ ! -f "$RENDERS_DIR/$render" ]; then
        echo "✗ FAIL: Missing $render"
        echo ""
        echo "Generate renders with: make renders"
        exit 1
    fi
    echo "  ✓ Found: $render"
done
echo ""

# Step 2: Claude Analysis (Interactive)
echo "Step 2: CLAUDE ANALYSIS"
echo "--------------------------------------------"
echo "OPEN the render: $RENDERS_DIR/hull_v6_simple.png"
echo ""
echo "Please describe what you observe:"
echo "  - List SPECIFIC geometric features (slots, curves, dimensions)"
echo "  - Note anything MISSING that should be visible"
echo "  - State confidence level (low/medium/high)"
echo ""
read -p "Claude observations: " claude_obs

if [ -z "$claude_obs" ]; then
    echo "✗ FAIL: Claude observations required (cannot be empty)"
    exit 1
fi
echo ""

# Step 3: Gemini Independent Verification
echo "Step 3: GEMINI INDEPENDENT VERIFICATION"
echo "--------------------------------------------"
echo "Gemini will now analyze the same render independently..."
echo ""
python3 ../../scripts/gemini_verify.py \
    --image "$RENDERS_DIR/hull_v6_simple.png" \
    --query "Describe the hull geometry visible in this render. Are frame mounting slots visible? If so, describe their position and orientation. List all geometric features you can identify. Be specific about what you see."

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ FAIL: Gemini verification failed"
    exit 1
fi
echo ""

# Step 4: Comparison
echo "Step 4: VERIFICATION COMPARISON"
echo "--------------------------------------------"
echo "Compare Claude and Gemini observations above."
echo ""
read -p "Do Claude and Gemini observations AGREE on visible features? (yes/no): " agree
if [ "$agree" != "yes" ]; then
    echo "✗ FAIL: Observations do not agree - human review required"
    echo ""
    echo "Action required: Investigate discrepancy before proceeding"
    exit 1
fi
echo ""

# Step 5: Critical Feature Confirmation
echo "Step 5: CRITICAL FEATURE VERIFICATION"
echo "--------------------------------------------"
echo "Based on your observations and Gemini's analysis:"
echo ""
read -p "Are frame mounting slots VISIBLE in the hull render? (yes/no): " slots_visible
if [ "$slots_visible" != "yes" ]; then
    echo "✗ FAIL: Frame slots not visible - geometry error detected"
    echo ""
    echo "This is a CRITICAL error (see claude.md frame slot bug Feb 2026)"
    echo "Action required: Debug hull_simple.scad slot geometry"
    exit 1
fi
echo ""

# Step 6: Frame Analysis
echo "Step 6: FRAME VERIFICATION"
echo "--------------------------------------------"
echo "Analyzing frame geometry..."
echo ""
python3 ../../scripts/gemini_verify.py \
    --image "$RENDERS_DIR/frame_v6_simple.png" \
    --query "Describe the frame structure. Are pivot balls visible? If so, describe their positions. Describe the rail geometry and any structural members you can see."

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ FAIL: Frame verification failed"
    exit 1
fi
echo ""
read -p "Are pivot balls visible and correctly positioned? (yes/no): " balls_visible
if [ "$balls_visible" != "yes" ]; then
    echo "✗ FAIL: Pivot balls not visible or incorrectly positioned"
    exit 1
fi
echo ""

# Step 7: Assembly Verification
echo "Step 7: ASSEMBLY FIT VERIFICATION"
echo "--------------------------------------------"
echo "Analyzing assembly fit..."
echo ""
python3 ../../scripts/gemini_verify.py \
    --image "$RENDERS_DIR/assembly_v6_simple.png" \
    --query "Does the frame appear to fit correctly in the hull? Are the pivot balls aligned with hull slots? Describe the assembly and note any clearance issues or interference you can see."

if [ $? -ne 0 ]; then
    echo ""
    echo "✗ FAIL: Assembly verification failed"
    exit 1
fi
echo ""
read -p "Does assembly appear correct (frame fits in hull)? (yes/no): " assembly_ok
if [ "$assembly_ok" != "yes" ]; then
    echo "✗ FAIL: Assembly verification failed"
    exit 1
fi
echo ""

# Success
echo "============================================"
echo "✓ DUAL-AI VISUAL VERIFICATION PASSED"
echo "============================================"
echo ""
echo "All verification gates passed:"
echo "  ✓ Claude observations documented"
echo "  ✓ Gemini independent verification complete"
echo "  ✓ Observations agree"
echo "  ✓ Frame slots visible"
echo "  ✓ Pivot balls visible and positioned"
echo "  ✓ Assembly fit verified"
echo ""
echo "Next step: Complete VERIFICATION_LOG.md with observations"
echo "Then proceed with test print preparation"
exit 0
