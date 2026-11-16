"""
evaluation.py - Automated Benchmarking and Analysis

"""

import copy
import time
import statistics
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple

from network import load_network
from dijkstra import dijkstra_search
from astar import astar_search


def create_disrupted_network(
    base_graph: Dict[str, List[dict]],
    blocked_pairs: List[Tuple[str, str]]
) -> Dict[str, List[dict]]:
    """Returns a deep copy of base_graph with blocked city pairs removed in both directions."""
    disrupted = copy.deepcopy(base_graph)
    for loc1, loc2 in blocked_pairs:
        if loc1 in disrupted:
            disrupted[loc1] = [e for e in disrupted[loc1] if e["destination"] != loc2]
        if loc2 in disrupted:
            disrupted[loc2] = [e for e in disrupted[loc2] if e["destination"] != loc1]
    return disrupted


def calculate_route_totals(graph: Dict[str, List[dict]], path: List[str]) -> Tuple[float, float]:
    """Calculates both total travel time (h) and transport cost along the returned path."""
    if not path or len(path) < 2:
        return 0.0, 0.0

    total_time, total_cost = 0.0, 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edges = [e for e in graph.get(u, []) if e["destination"] == v]
        if edges:
            total_time += edges[0]["time"]
            total_cost += edges[0]["cost"]
    return total_time, total_cost


def benchmark_single_query(
    search_func,
    graph: Dict[str, List[dict]],
    start: str,
    goal: str,
    weight: str,
    iterations: int = 100
) -> dict:
    """Executes repeated runs to measure latency statistics and search metrics."""
    timings = []
    path, total_weight, nodes_explored = [], float("inf"), 0

    for _ in range(iterations):
        t0 = time.perf_counter()
        path, total_weight, nodes_explored = search_func(graph, start, goal, weight)
        t1 = time.perf_counter()
        timings.append((t1 - t0) * 1000.0)

    total_time, total_cost = calculate_route_totals(graph, path)

    return {
        "path": path,
        "weight": total_weight,
        "nodes_explored": nodes_explored,
        "mean_ms": statistics.mean(timings),
        "std_ms": statistics.stdev(timings) if len(timings) > 1 else 0.0,
        "total_time": total_time,
        "total_cost": total_cost,
    }


def run_gaza_disruption_suite(base_graph: Dict[str, List[dict]]) -> pd.DataFrame:
    """Evaluates Dubai -> Gaza across normal operations and 3 disruption scenarios."""
    scenarios = [
        ("S1", "Baseline (Min Time)", "time", []),
        ("S2", "Baseline (Min Cost)", "cost", []),
        ("S3", "Airspace Closure (All 3 Air Links Blocked)", "time", [
            ("Dubai", "Amman"), ("Dubai", "Riyadh"), ("Riyadh", "Amman")
        ]),
        ("S4", "Levant Corridor Disruption (Amman/Aqaba-Al Arish Blocked)", "time", [
            ("Amman", "Al Arish"), ("Aqaba", "Al Arish")
        ]),
        ("S5", "Gaza Chokepoint Severed (Al Arish-Gaza Blocked)", "time", [
            ("Al Arish", "Gaza")
        ]),
    ]

    records = []
    for sid, desc, weight, blocked in scenarios:
        test_graph = create_disrupted_network(base_graph, blocked)
        for algo_name, algo_fn in [("Dijkstra", dijkstra_search), ("A*", astar_search)]:
            res = benchmark_single_query(algo_fn, test_graph, "Dubai", "Gaza", weight)
            records.append({
                "Scenario": sid,
                "Description": desc,
                "Algorithm": algo_name,
                "Path": " -> ".join(res["path"]) if res["path"] else "UNREACHABLE",
                "Optimal Weight": round(res["weight"], 2) if res["weight"] != float("inf") else "inf",
                "Nodes Explored": res["nodes_explored"],
                "Total Time (h)": round(res["total_time"], 2),
                "Total Cost": round(res["total_cost"], 2),
                "Runtime (ms)": f"{res['mean_ms']:.4f} ± {res['std_ms']:.4f}",
            })

    df = pd.DataFrame(records)
    df.to_csv("benchmark_results.csv", index=False)
    return df


def run_all_pairs_pruning_benchmark(base_graph: Dict[str, List[dict]]) -> pd.DataFrame:
    """Benchmarks all 56 origin-destination pairs to quantify A* state-space pruning."""
    nodes = list(base_graph.keys())
    pair_records = []

    for u in nodes:
        for v in nodes:
            if u == v:
                continue
            for weight in ("time", "cost"):
                _, dw, dn = dijkstra_search(base_graph, u, v, weight)
                _, aw, an = astar_search(base_graph, u, v, weight)
                pair_records.append({
                    "Origin": u,
                    "Destination": v,
                    "Weight": weight,
                    "Optimal Value": dw,
                    "Dijkstra Nodes": dn,
                    "A* Nodes": an,
                    "Nodes Saved": dn - an,
                })

    df_pairs = pd.DataFrame(pair_records)
    df_pairs.to_csv("all_pairs_pruning.csv", index=False)
    return df_pairs


def generate_report_charts(df_pairs: pd.DataFrame):
    """Generates a bar chart comparing nodes explored on representative regional corridors."""
    sample_routes = [
        ("Dubai", "Amman", "time"),
        ("Riyadh", "Amman", "cost"),
        ("Jeddah", "Dubai", "cost"),
        ("Amman", "Abu Dhabi", "cost"),
        ("Riyadh", "Gaza", "cost"),
        ("Dubai", "Gaza", "time"),
    ]

    labels, d_vals, a_vals = [], [], []
    for u, v, w in sample_routes:
        row = df_pairs[(df_pairs["Origin"] == u) & (df_pairs["Destination"] == v) & (df_pairs["Weight"] == w)].iloc[0]
        labels.append(f"{u}->{v}\n({w})")
        d_vals.append(row["Dijkstra Nodes"])
        a_vals.append(row["A* Nodes"])

    x = range(len(labels))
    plt.figure(figsize=(10, 5))
    plt.bar([i - 0.2 for i in x], d_vals, width=0.4, label="Dijkstra (Uniform Cost)", color="#e74c3c")
    plt.bar([i + 0.2 for i in x], a_vals, width=0.4, label="A* Search (Haversine Heuristic)", color="#2ecc71")

    plt.ylabel("Unique Nodes Explored")
    plt.title("Search Space Efficiency Across Regional Humanitarian Corridors")
    plt.xticks(x, labels)
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("search_comparison.png", dpi=300)


if __name__ == "__main__":
    graph = load_network()

    print("\n=== TABLE 1: DUBAI -> GAZA DISRUPTION SCENARIOS ===")
    df_gaza = run_gaza_disruption_suite(graph)
    print(df_gaza.to_string(index=False))

    print("\n=== TABLE 2: ALL-PAIRS NETWORK PRUNING SUMMARY (112 QUERIES) ===")
    df_all = run_all_pairs_pruning_benchmark(graph)
    print(f"Mean Nodes Explored — Dijkstra: {df_all['Dijkstra Nodes'].mean():.2f} | A*: {df_all['A* Nodes'].mean():.2f}")
    print(f"Queries where A* expanded strictly fewer nodes: {(df_all['Nodes Saved'] > 0).sum()} / {len(df_all)}")

    generate_report_charts(df_all)
    print("\n[+] Exported benchmark_results.csv, all_pairs_pruning.csv, and search_comparison.png")
