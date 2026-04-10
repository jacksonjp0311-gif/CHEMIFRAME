from chemiframe import planner, compiler
from chemiframe.intent.schema import default_intent


def test_compiler_emits_xdl():
    route = planner.plan(default_intent())
    xdl = compiler.lower_to_xdl(route)
    assert "<procedure" in xdl