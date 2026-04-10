from chemiframe.blueprints.coupling import ArylCouplingBlueprint
from chemiframe.intent.schema import default_intent


def test_aryl_blueprint_admits_default_intent():
    bp = ArylCouplingBlueprint()
    assert bp.admissibility(default_intent()) is True