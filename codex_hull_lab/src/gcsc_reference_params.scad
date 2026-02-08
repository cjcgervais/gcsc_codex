// Canonical interface geometry inherited from verified GCSC v5.3 assembly.
// These values define non-negotiable frame/slot compatibility anchors.

REFERENCE_PIVOT_Y = 33.0;
REFERENCE_PIVOT_Z = 38.0;

REFERENCE_SLOT_DIAMETER = 7.5;
REFERENCE_BALL_DIAMETER = 7.25;
REFERENCE_SLOT_ENTRY_Z = 45.0;

REFERENCE_FRAME_SPACING = 16.0;
REFERENCE_FRAME_BOTTOM_Z = 17.0;

REFERENCE_SLOT_CLEARANCE_TARGET = 0.12;

REFERENCE_FOOT_PAD_DIAMETER = 8.0;
REFERENCE_FOOT_PAD_DEPTH = 1.5;

// The legacy v5.3 reference files use rim/slot-entry at Z=45.
// This hull lab keeps rim plane at model Z=0, so map via this offset.
REFERENCE_COORDINATE_RIM_Z = REFERENCE_SLOT_ENTRY_Z;
REFERENCE_MODEL_RIM_Z = 0.0;

function gcsc_reference_to_model_z(z_ref) =
    z_ref - REFERENCE_COORDINATE_RIM_Z + REFERENCE_MODEL_RIM_Z;

function gcsc_model_to_reference_z(z_model) =
    z_model - REFERENCE_MODEL_RIM_Z + REFERENCE_COORDINATE_RIM_Z;

function gcsc_reference_pivot_seat_model_z() =
    gcsc_reference_to_model_z(REFERENCE_PIVOT_Z);

function gcsc_reference_slot_entry_model_z() =
    gcsc_reference_to_model_z(REFERENCE_SLOT_ENTRY_Z);

function gcsc_slot_ball_clearance_diameter() =
    REFERENCE_SLOT_DIAMETER - REFERENCE_BALL_DIAMETER;

function gcsc_slot_ball_clearance_radial() =
    gcsc_slot_ball_clearance_diameter() / 2;

module gcsc_reference_guardrails() {
    radial_clearance = gcsc_slot_ball_clearance_radial();
    assert(
        abs(REFERENCE_FRAME_SPACING - 16.0) < 0.001,
        "Reference spacing invariant violated. Expected +/-16 mm slot columns."
    );
    assert(
        abs(REFERENCE_SLOT_DIAMETER - 7.5) < 0.001,
        "Reference slot diameter invariant violated. Expected 7.5 mm."
    );
    assert(
        abs(REFERENCE_PIVOT_Y - 33.0) < 0.001 && abs(REFERENCE_PIVOT_Z - 38.0) < 0.001,
        "Reference pivot invariant violated. Expected Y=33 mm and Z=38 mm in reference coordinates."
    );
    assert(
        abs(radial_clearance - REFERENCE_SLOT_CLEARANCE_TARGET) <= 0.01,
        str(
            "Reference radial clearance drifted. Current=",
            radial_clearance,
            " target=",
            REFERENCE_SLOT_CLEARANCE_TARGET
        )
    );
}
