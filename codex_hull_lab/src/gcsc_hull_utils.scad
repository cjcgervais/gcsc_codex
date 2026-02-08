// Shared helper utilities for hull generation.

function gcsc_clamp(v, lo, hi) = min(max(v, lo), hi);
function gcsc_clamp01(v) = gcsc_clamp(v, 0, 1);
function gcsc_lerp(a, b, t) = a + (b - a) * t;
function gcsc_safe(v, fallback) = is_undef(v) ? fallback : v;

// Cubic smoothstep in [edge0, edge1].
function gcsc_smoothstep(edge0, edge1, x) =
    let(t = gcsc_clamp01((x - edge0) / max(edge1 - edge0, 0.0001)))
    t * t * (3 - 2 * t);
