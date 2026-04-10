from chemiframe.intent.schema import default_intent
from chemiframe.demo_support import run_pipeline

report = run_pipeline(default_intent(), simulate=False)

print("INTENT:", report["intent"])
print("ROUTE:", report["route"])
print("CONTRACTS:", report["contracts"])
print("ARTIFACT PATH:", report["artifact_path"])
print("CONTRACT PATH:", report["contract_path"])
print("TRACE PATH:", report["trace_path"])
print("REPORT PATH:", report["report_path"])
print("RUN ID:", report["run_id"])
print("STATUS:", report["status"])
print("SIMULATED:", report["simulated"])