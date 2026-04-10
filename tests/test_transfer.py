from chemiframe.verify.transfer_admissibility import check


def test_transfer_check_false_when_missing_requirements():
    result = check({"finite_route_ok": True})
    assert result["transfer_admissible"] is False