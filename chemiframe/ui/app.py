from typing import Any, Dict


def initial_ui_state() -> Dict[str, Any]:
    return {
        "intent": {},
        "blueprint": None,
        "route_graph": None,
        "contracts": {},
        "compiled_artifact": None,
        "simulation_events": [],
        "transfer_contract": None,
        "sequence_contract": None,
        "hybrid_contract": None,
        "execution_status": "idle",
        "trace_id": None,
        "feature_surfaces": [],
    }