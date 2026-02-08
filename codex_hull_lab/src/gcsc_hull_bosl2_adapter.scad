// BOSL2 integration boundary for codex_hull_lab.
// Keep BOSL2-specific includes/wrappers here so hull logic stays readable.

include <../../02_Production_BOSL2/lib/BOSL2/std.scad>

module gcsc_require_bosl2() {
    assert(
        !is_undef(_BOSL2_STD),
        "BOSL2 missing. Expected include path ../../02_Production_BOSL2/lib/BOSL2/std.scad. If unavailable, vendor BOSL2 into codex_hull_lab/third_party/BOSL2 and update gcsc_hull_bosl2_adapter.scad."
    );
}

module gcsc_move(v = [0, 0, 0]) {
    gcsc_require_bosl2();
    move(v) children();
}

module gcsc_xrot(a = 0) {
    gcsc_require_bosl2();
    xrot(a) children();
}

module gcsc_yrot(a = 0) {
    gcsc_require_bosl2();
    yrot(a) children();
}

module gcsc_zrot(a = 0) {
    gcsc_require_bosl2();
    zrot(a) children();
}
