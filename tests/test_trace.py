from chemiframe.runtime.trace import store, load


def test_trace_store_and_load(tmp_path):
    run = {"run_id": "trace_test_001", "status": "completed"}
    path = store(run, artifacts_root=str(tmp_path))
    loaded = load("trace_test_001", artifacts_root=str(tmp_path))
    assert loaded["status"] == "completed"