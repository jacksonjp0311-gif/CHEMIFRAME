from chemiframe.adapters.simulator import simulator


def test_simulator_returns_simulated_run():
    run = simulator.execute("<procedure />")
    assert run["simulated"] is True