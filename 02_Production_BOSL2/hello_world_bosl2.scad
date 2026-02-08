// GCSC2 Phase 2 - Hello World BOSL2 Test
// Purpose: Verify BOSL2 library is installed and working
// Expected: Simple lofted shape renders without errors

include <lib/BOSL2/std.scad>
include <lib/BOSL2/skin.scad>

// Simple test: Create a basic lofted shape using skin()
// This proves BOSL2 functions are accessible

// Define 3 cross-sections at different Z heights
profile1 = circle(d=20, $fn=32);   // Bottom (small circle)
profile2 = circle(d=40, $fn=32);   // Middle (large circle)
profile3 = circle(d=25, $fn=32);   // Top (medium circle)

// Position profiles in 3D space
profiles_3d = [
    path3d(profile1, 0),      // Z=0
    path3d(profile2, 20),     // Z=20
    path3d(profile3, 40)      // Z=40
];

// Loft surface between profiles
skin(profiles_3d, slices=5, method="tangent");

echo("=== BOSL2 HELLO WORLD TEST ===");
echo("If this renders without errors, BOSL2 is working correctly!");
echo("Expected: Vase-like shape with 3 circular cross-sections");
