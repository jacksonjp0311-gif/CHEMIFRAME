from chemiframe.runtime.orchestrator import execute


def test_execute_returns_run():
    run = execute("<procedure />")
    assert run["status"] == "completed"