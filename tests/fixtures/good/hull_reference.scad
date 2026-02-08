// GCSC2 Test Fixture: Known-good hull shape
// Simple convex hull that should always pass validation

hull() {
    translate([0, 0, 0]) sphere(r=10, $fn=32);
    translate([50, 0, 0]) sphere(r=5, $fn=32);
    translate([25, 15, 0]) sphere(r=8, $fn=32);
    translate([25, -15, 0]) sphere(r=8, $fn=32);
}
