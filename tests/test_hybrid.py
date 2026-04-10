from chemiframe.verify.hybrid_admissibility import check


def test_hybrid_check_requires_bounded_coupling():
    result = check({
        "finite_route_ok": True,
        "detectability_ok": True,
        "dec_representation_ok": True,
        "artifact_visibility_ok": True,
        "trace_continuity_ok": True,
        "bounded_coupling_ok": False,
    })
    assert result["transfer_admissible"] is False