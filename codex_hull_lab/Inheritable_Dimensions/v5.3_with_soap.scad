// GCSC v5.3 Assembly with Soap Bar - For Reference Image Generation
// Article 0.6 - Visual Reference Requirements (FR-0 Proof - Soap Elevation)
//
// This demonstrates THE CORNERSTONE: Soap elevated ABOVE hull floor,
// resting on frame top member edges with minimal contact.

// Hull positioned at origin
translate([0, 0, 0])
    import("STL_files/GCSC_Hull_v5.3.stl");

// Frame positioned at z_pivot_seat height (38mm per Final_GCSC_Assembly.md)
translate([0, 0, 38])
    import("STL_files/CF_Frame_v5.3_infill.stl");

// Soap bar primitive (standard bar soap dimensions)
// Positioned to rest ACROSS frame top members
// This proves FR-0: Soap ELEVATED, not touching hull floor
color("ivory", 0.8)
translate([0, 0, 55])  // Approximate height: pivot at 38mm + frame height + soap elevation
    cube([100, 50, 25], center=true);
