from chemiframe.intent.parser import load_intent
from chemiframe.demo_support import run_pipeline

intent = load_intent("examples/intent_hybrid_01.json")
report = run_pipeline(intent, simulate=True)

print("HYBRID INTENT:", report["intent"])
print("HYBRID ROUTE:", report["route"])
print("HYBRID CONTRACTS:", report["contracts"])
print("ARTIFACT PATH:", report["artifact_path"])
print("CONTRACT PATH:", report["contract_path"])
print("TRACE PATH:", report["trace_path"])
print("REPORT PATH:", report["report_path"])
print("RUN ID:", report["run_id"])
print("STATUS:", report["status"])
print("SIMULATED:", report["simulated"])