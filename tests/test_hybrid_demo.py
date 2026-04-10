from chemiframe.intent.parser import load_intent
from chemiframe.demo_support import run_pipeline


def test_hybrid_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    intent = load_intent(r"C:\Users\jacks\OneDrive\Desktop\CHEMIFRAME\examples\intent_hybrid_01.json")
    report = run_pipeline(intent, simulate=True)
    assert report["simulated"] is True
    assert report["route"]["family"] == "hybrid_chemo_bio"