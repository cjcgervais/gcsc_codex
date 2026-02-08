// GCSC v5.3 Pivot Action - For Reference Image Generation
// Article 0.6 - Visual Reference Requirements (FR-2 Proof - Gimbal Mechanism)
//
// This demonstrates the gimbal swing capability: Frame can tilt/rotate
// relative to hull, creating the gripping bite through angular displacement.

// Hull positioned at origin
translate([0, 0, 0])
    import("STL_files/GCSC_Hull_v5.3.stl");

// Frame positioned at z_pivot_seat height (38mm) but ROTATED
// to show gimbal action capability
// Rotation around Y-axis (port-starboard, through pivot balls)
translate([0, 0, 38])
    rotate([0, 25, 0])  // 25° tilt to demonstrate swing range
        import("STL_files/CF_Frame_v5.3_infill.stl");

// Note: In real use, frame would tilt based on soap placement
// creating moment arm that engages edge geometry for gripping bite
