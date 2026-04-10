from chemiframe import planner
from chemiframe.verify.contracts import run_preflight
from chemiframe.intent.schema import default_intent


def test_preflight_ok():
    route = planner.plan(default_intent())
    result = run_preflight(route)
    assert result["ok"] is True