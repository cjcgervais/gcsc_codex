// GCSC v5.3 Assembly for Reference Image Generation
// Article 0.6 - Visual Reference Requirements
// Temporary file for generating canonical reference images

// Hull positioned at origin
translate([0, 0, 0])
    import("STL_files/GCSC_Hull_v5.3.stl");

// Frame positioned at z_pivot_seat height (38mm per Final_GCSC_Assembly.md)
translate([0, 0, 38])
    import("STL_files/CF_Frame_v5.3_infill.stl");

// Anchor (optional, for functional context)
// translate([0, 0, z_anchor])
//     import("STL_files/GCSC_Danforth_Anchor_v1.2.stl");
