// GCSC2 Hull v6.0-minimalist
// Great Canadian Soap Canoe - Phase 1 Minimalist Prototype
//
// Design Approach: Simple 5-point hull() geometry for rapid iteration
// Goal: Validate proportions and frame attachment before BOSL2 migration
//
// ============================================
// USAGE:
//   F5 - Quick preview
//   F6 - Full render
//   make hull.stl - Export STL
// ============================================

use <modules/hull_simple.scad>

// Render the complete hull
hull_complete();

// ============ DESIGN NOTES ============
// This is Phase 1 of the Option D hybrid approach:
//   - Minimalist CSG using hull() operator
//   - 5-10 parameters for rapid iteration
//   - Focus on proportions and printability
//   - Frame attachment validation
//
// Next Phase: Migrate to BOSL2 with bezier stations
// for production-quality fair curves
