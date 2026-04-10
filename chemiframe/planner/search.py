from typing import Any, Dict
from chemiframe.blueprints.coupling import ArylCouplingBlueprint
from chemiframe.blueprints.sequence_assembly import SequenceAssemblyBlueprint
from chemiframe.blueprints.hybrid_interface import HybridInterfaceBlueprint


def select_blueprint(intent: Dict[str, Any]):
    candidates = [
        HybridInterfaceBlueprint(),
        SequenceAssemblyBlueprint(),
        ArylCouplingBlueprint(),
    ]
    for candidate in candidates:
        if candidate.admissibility(intent):
            return candidate
    return ArylCouplingBlueprint()