"""
evaluation.py - Automated Benchmarking & Disruption Evaluation

"""

import csv
import copy
import time
import statistics
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from network import load_network, load_representative_network
from dijkstra import dijkstra_search
from astar import astar_search

DATA_DIR = Path(__file__).resolve().parent / "data"


def create_disrupted_synthetic(base_graph, blocked_pairs):
    """Removes blocked city pairs bidirectionally on a deep copy of the synthetic graph."""
    disrupted = copy.deepcopy(base_graph)
    for loc1, loc2 in blocked_pairs:
        if loc1 in disrupted:
            disrupted[loc1] = [e for e in disrupted[loc1] if e["destination"] != loc2]
        if loc2 in disrupted:
            disrupted[loc2] = [e for e in disrupted[loc2] if e["destination"] != loc1]
    return disrupted


def apply_hrp_scenario(base_graph, scenario_id, filename="hrp_disruption_scenarios.csv"):
    """
    Applies S0-S9 disruptions (CLOSE, TIME_MULT, COST_MULT, COMBINE)
    on a deep copy of the representative Dubai Humanitarian graph.
    """
    graph = copy.deepcopy(base_graph)
    if scenario_id == "S0":
        return graph

    with open(DATA_DIR / filename, "r", newline="", encoding="utf-8-sig") as file:
        rows = list(csv.DictReader(file))

    target_ids = [scenario_id]
    actions = []
    while target_ids:
        curr = target_ids.pop(0)
        for r in rows:
            if r["scenario_id"].strip() == curr:
                if r["action"].strip() == "COMBINE":
                    target_ids.extend([s.strip() for s in r["value"].split(";")])
                else:
                    actions.append(r)

    for act in actions:
        action_type = act["action"].strip()
        leg_id = act["leg_id"].strip()
        val = float(act["value"]) if act["value"].strip() else None

        for u in graph:
            if action_type == "CLOSE":
                graph[u] = [e for e in graph[u] if e.get("leg_id") != leg_id]
            elif action_type == "TIME_MULT":
                for e in graph[u]:
                    if e.get("leg_id") == leg_id:
                        e["time"] *= val
            elif action_type == "COST_MULT":
                for e in graph[u]:
                    if e.get("leg_id") == leg_id:
                        e["cost"] *= val

    return graph


def calculate_route_totals(graph, path, objective="time"):
    """Computes total time, total cost, and total risk along a returned path."""
    if not path or len(path) < 2:
        return 0.0, 0.0, 0.0

    tot_time, tot_cost, tot_risk = 0.0, 0.0, 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        matches = [e for e in graph.get(u, []) if e["destination"] == v]
        if matches:
            edge = min(matches, key=lambda x: x.get(objective, 0.0))
            tot_time += float(edge.get("time", 0.0))
            tot_cost += float(edge.get("cost", 0.0))
            tot_risk += float(edge.get("risk", 0.0))
    return tot_time, tot_cost, tot_risk


def benchmark_query(search_fn, graph, start, goal, weight, iterations=100):
    """Measures mean latency, std dev, and path metrics over repeated runs."""
    timings = []
    path, total_weight, nodes_explored = [], float("inf"), 0

    for _ in range(iterations):
        t0 = time.perf_counter()
        path, total_weight, nodes_explored = search_fn(graph, start, goal, weight)
        timings.append((time.perf_counter() - t0) * 1000.0)

    tot_t, tot_c, tot_r = calculate_route_totals(graph, path, weight)
    return {
        "path": path,
        "weight": total_weight,
        "nodes": nodes_explored,
        "time_h": tot_t,
        "cost": tot_c,
        "risk": tot_r,
        "mean_ms": statistics.mean(timings),
        "std_ms": statistics.stdev(timings) if len(timings) > 1 else 0.0,
    }


def run_synthetic_benchmarks():
    """Evaluates Dataset 1 (8-node synthetic network: Dubai -> Gaza)."""
    base_graph = load_network()
    scenarios = [
        ("S1", "Baseline (Min Time)", "time", []),
        ("S2", "Baseline (Min Cost)", "cost", []),
        ("S3", "Airspace Closure", "time", [("Dubai", "Amman"), ("Dubai", "Riyadh"), ("Riyadh", "Amman")]),
        ("S4", "Levant Disruption", "time", [("Amman", "Al Arish"), ("Aqaba", "Al Arish")]),
        ("S5", "Gaza Chokepoint Severed", "time", [("Al Arish", "Gaza")]),
    ]

    records = []
    for sid, desc, w, blocked in scenarios:
        g = create_disrupted_synthetic(base_graph, blocked)
        for algo_name, fn in [("Dijkstra", dijkstra_search), ("A*", astar_search)]:
            res = benchmark_query(fn, g, "Dubai", "Gaza", w)
            records.append({
                "Scenario": sid,
                "Description": desc,
                "Algorithm": algo_name,
                "Path": " -> ".join(res["path"]) if res["path"] else "UNREACHABLE",
                "Optimal Weight": round(res["weight"], 2) if res["weight"] != float("inf") else "inf",
                "Nodes Explored": res["nodes"],
                "Total Time (h)": round(res["time_h"], 2),
                "Total Cost": round(res["cost"], 2),
                "Runtime (ms)": f"{res['mean_ms']:.4f} ± {res['std_ms']:.4f}",
            })

    df = pd.DataFrame(records)
    df.to_csv("synthetic_benchmark_results.csv", index=False)
    return df


def run_representative_benchmarks():
    """Evaluates Dataset 2 (23-node Dubai Humanitarian network: IHC -> ELO across S0-S9)."""
    base_graph, _ = load_representative_network()
    scenarios = [
        ("S0", "Baseline (All legs open)"),
        ("S1", "Port Sudan airport closed"),
        ("S2", "Southern Red Sea transit suspended"),
        ("S3", "Metema-Gallabat crossing closed"),
        ("S4", "Omdurman-El Obeid road blocked"),
        ("S5", "El Obeid airport closed"),
        ("S6", "Rainy season road degradation (1.6x time)"),
        ("S7", "Argeen crossing congestion (2.5x time)"),
        ("S8", "Insurance spike on Red Sea (1.8x cost)"),
        ("S9", "Compound Stress Test (S1 + S2)"),
    ]
    objectives = ["time", "cost", "risk"]

    records = []
    for sid, sname in scenarios:
        g = apply_hrp_scenario(base_graph, sid)
        for obj in objectives:
            for algo_name, fn in [("Dijkstra", dijkstra_search), ("A*", astar_search)]:
                res = benchmark_query(fn, g, "IHC", "ELO", obj)
                records.append({
                    "Scenario": sid,
                    "Scenario Name": sname,
                    "Objective": obj,
                    "Algorithm": algo_name,
                    "Route": " -> ".join(res["path"]) if res["path"] else "UNREACHABLE",
                    "Objective Value": round(res["weight"], 2) if res["weight"] != float("inf") else "inf",
                    "Nodes Explored": res["nodes"],
                    "Total Time (h)": round(res["time_h"], 1),
                    "Total Cost ($/t)": round(res["cost"], 1),
                    "Cumulative Risk": round(res["risk"], 1),
                    "Runtime (ms)": f"{res['mean_ms']:.4f} ± {res['std_ms']:.4f}",
                })

    df = pd.DataFrame(records)
    df.to_csv("dh_benchmark_results.csv", index=False)

    # Generate comparison chart for 'time' objective across S0-S9
    t_df = df[df["Objective"] == "time"]
    sids = [s[0] for s in scenarios]
    d_nodes = t_df[t_df["Algorithm"] == "Dijkstra"]["Nodes Explored"].tolist()
    a_nodes = t_df[t_df["Algorithm"] == "A*"]["Nodes Explored"].tolist()

    x = range(len(sids))
    plt.figure(figsize=(10, 5))
    plt.bar([i - 0.2 for i in x], d_nodes, width=0.4, label="Dijkstra", color="#e74c3c")
    plt.bar([i + 0.2 for i in x], a_nodes, width=0.4, label="A* Search (Haversine Heuristic)", color="#2ecc71")
    plt.xticks(x, sids)
    plt.xlabel("Dubai Humanitarian Disruption Scenarios (S0 - S9)")
    plt.ylabel("Unique Nodes Explored")
    plt.title("Dubai Humanitarian Corridor (IHC -> ELO): Dijkstra vs A* Node Expansions")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("dh_search_comparison.png", dpi=300)

    return df


if __name__ == "__main__":
    print("\n=== DATASET 1: SYNTHETIC NETWORK BENCHMARKS (Dubai -> Gaza) ===")
    df_syn = run_synthetic_benchmarks()
    print(df_syn.to_string(index=False))

    print("\n=== DATASET 2: DUBAI HUMANITARIAN BENCHMARKS (IHC -> ELO, S0-S9) ===")
    df_dh = run_representative_benchmarks()
    print(df_dh.to_string(index=False))

    print("\n[+] Exported synthetic_benchmark_results.csv, dh_benchmark_results.csv, and dh_search_comparison.png")
