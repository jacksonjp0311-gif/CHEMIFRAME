from chemiframe import planner
from chemiframe.intent.schema import default_intent


def test_planner_returns_route():
    route = planner.plan(default_intent())
    assert "steps" in route and len(route["steps"]) > 0