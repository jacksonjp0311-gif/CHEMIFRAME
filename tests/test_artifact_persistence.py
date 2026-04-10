from pathlib import Path
from chemiframe.intent.schema import default_intent
from chemiframe.demo_support import run_pipeline


def test_pipeline_persists_artifacts(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    report = run_pipeline(default_intent(), simulate=False)

    assert Path(report["artifact_path"]).exists()
    assert Path(report["contract_path"]).exists()
    assert Path(report["trace_path"]).exists()
    assert Path(report["report_path"]).exists()