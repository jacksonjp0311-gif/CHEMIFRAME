from chemiframe.verify.sequence_admissibility import check


def test_sequence_check_true_when_order_is_preserved():
    result = check({
        "finite_route_ok": True,
        "detectability_ok": True,
        "dec_representation_ok": True,
        "artifact_visibility_ok": True,
        "trace_continuity_ok": True,
        "ordered_steps_ok": True,
    })
    assert result["transfer_admissible"] is True