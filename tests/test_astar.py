"""
Unit and integration tests for astar.py across both datasets,
optimisation weights, disruption scenarios, and edge cases.
"""

import copy
import csv
import math
from pathlib import Path

from network import load_network, load_representative_network
from dijkstra import dijkstra_search
from astar import astar_search, register_coordinates


def apply_disruption_scenario(graph, scenario_id):
    """Applies a scenario from data/hrp_disruption_scenarios.csv to a deep copy of graph."""
    disrupted = copy.deepcopy(graph)
    if scenario_id == "S0":
        return disrupted

    csv_path = Path(__file__).resolve().parent.parent / "data" / "hrp_disruption_scenarios.csv"
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    target_rows = [r for r in rows if r["scenario_id"] == scenario_id]
    combined_ids = []
    for r in target_rows:
        if r["action"] == "COMBINE":
            combined_ids.extend(r["value"].split(";"))
    if combined_ids:
        target_rows = [r for r in rows if r["scenario_id"] in combined_ids]

    for r in target_rows:
        leg_id, action, val = r["leg_id"], r["action"], r["value"]
        for u in disrupted:
            if action == "CLOSE":
                disrupted[u] = [e for e in disrupted[u] if e.get("leg_id") != leg_id]
            elif action == "TIME_MULT":
                for e in disrupted[u]:
                    if e.get("leg_id") == leg_id:
                        e["time"] *= float(val)
            elif action == "COST_MULT":
                for e in disrupted[u]:
                    if e.get("leg_id") == leg_id:
                        e["cost"] *= float(val)
    return disrupted


def test_simulated_network_all_pairs():
    """Verify A* matches Dijkstra optimality on all 8-node simulated pairs."""
    graph = load_network()
    for start in graph:
        for goal in graph:
            for weight in ("time", "cost"):
                d_path, d_val, d_exp = dijkstra_search(graph, start, goal, weight)
                a_path, a_val, a_exp = astar_search(graph, start, goal, weight)
                assert math.isclose(d_val, a_val), f"Mismatch {start}->{goal} ({weight}): {d_val} vs {a_val}"
                assert a_exp <= d_exp, f"A* expanded more nodes than Dijkstra on {start}->{goal} ({weight})"
    print("[PASS] 8-node simulated network: all 128 queries optimal & admissible.")


def test_representative_network_all_pairs():
    """Verify A* matches Dijkstra across all 23-node Dubai Humanitarian pairs and weights."""
    graph, _ = load_representative_network()
    fewer_nodes = 0
    for start in graph:
        for goal in graph:
            for weight in ("time", "cost", "risk"):
                d_path, d_val, d_exp = dijkstra_search(graph, start, goal, weight)
                a_path, a_val, a_exp = astar_search(graph, start, goal, weight)
                if math.isinf(d_val):
                    assert math.isinf(a_val) and a_path == []
                else:
                    assert math.isclose(d_val, a_val), f"Mismatch {start}->{goal} ({weight}): {d_val} vs {a_val}"
                    assert a_exp <= d_exp, f"A* expanded more nodes on {start}->{goal} ({weight})"
                    if a_exp < d_exp:
                        fewer_nodes += 1
    print(f"[PASS] 23-node Dubai Humanitarian network: all 1,587 queries optimal (A* pruned nodes in {fewer_nodes} cases).")


def test_disruption_scenarios():
    """Verify A* optimality and rerouting across scenarios S0-S9 for IHC -> ELO."""
    base_graph, _ = load_representative_network()
    for sid in [f"S{i}" for i in range(10)]:
        g = apply_disruption_scenario(base_graph, sid)
        for weight in ("time", "cost", "risk"):
            d_path, d_val, d_exp = dijkstra_search(g, "IHC", "ELO", weight)
            a_path, a_val, a_exp = astar_search(g, "IHC", "ELO", weight)
            assert math.isclose(d_val, a_val), f"Scenario {sid} ({weight}) mismatch: {d_val} vs {a_val}"
            assert a_exp <= d_exp
    print("[PASS] Disruption scenarios S0-S9 (IHC -> ELO): A* matched Dijkstra across time, cost, and risk.")


def test_edge_cases():
    """Verify edge cases: start==goal, unknown node, unreachable path, fallback h=0, invalid weight."""
    graph, _ = load_representative_network()

    assert astar_search(graph, "IHC", "IHC", "time") == (["IHC"], 0.0, 1)
    assert astar_search(graph, "UNKNOWN", "ELO", "time") == ([], float("inf"), 0)

    # Directed graph: ELO has no outgoing path back to IHC
    path, val, exp = astar_search(graph, "ELO", "IHC", "time")
    assert path == [] and math.isinf(val)

    # Fallback h = 0 when custom nodes lack coordinates
    custom = {
        "N1": [{"destination": "N2", "time": 3.0, "cost": 50.0}],
        "N2": [],
    }
    assert astar_search(custom, "N1", "N2", "time") == (["N1", "N2"], 3.0, 2)
    register_coordinates({"N1": (25.0, 55.0), "N2": (25.1, 55.1)})
    assert astar_search(custom, "N1", "N2", "time") == (["N1", "N2"], 3.0, 2)

    # Invalid weight check
    try:
        astar_search(graph, "IHC", "ELO", "invalid_metric")
        assert False, "Expected ValueError for invalid weight"
    except ValueError:
        pass

    print("[PASS] Edge cases & fallback behaviour verified.")


if __name__ == "__main__":
    test_simulated_network_all_pairs()
    test_representative_network_all_pairs()
    test_disruption_scenarios()
    test_edge_cases()
    print("\nAll A* tests passed successfully!")
