import copy
import streamlit as st
from network import load_network, load_representative_network
from evaluation import apply_hrp_scenario, calculate_route_totals

# Import team search algorithms
try:
    from dijkstra import dijkstra_search
except ImportError:
    dijkstra_search = None

try:
    from astar import astar_search
except ImportError:
    astar_search = None

st.set_page_config(page_title="Humanitarian Route Planner", page_icon="🧭", layout="wide")

st.title("Dubai Humanitarian Route Planner")
st.write("Interactive route planning and disruption simulation for humanitarian logistics.")

# Sidebar Configuration
st.sidebar.header("Route Parameters")

dataset_choice = st.sidebar.selectbox(
    "Dataset",
    ["Synthetic Network", "Dubai Humanitarian Network"]
)

if dataset_choice == "Synthetic Network":
    graph = load_network()
    location_names = {node: node for node in graph}
else:
    graph, location_info = load_representative_network()
    location_names = {
        node: details["name"]
        for node, details in location_info.items()
    }

locations = list(graph.keys())


def format_location(node):
    if dataset_choice == "Synthetic Network":
        return node
    return f"{location_names[node]} ({node})"


start_node = st.sidebar.selectbox(
    "Origin",
    locations,
    format_func=format_location
)

goal_node = st.sidebar.selectbox(
    "Destination",
    [node for node in locations if node != start_node],
    format_func=format_location
)

# Risk optimization is only available in the representative network.
weight_options = ["time", "cost"]
if dataset_choice == "Dubai Humanitarian Network":
    weight_options.append("risk")

weight_metric = st.sidebar.selectbox(
    "Optimization Goal",
    weight_options
)

if weight_metric == "time":
    metric_label = "Travel Time (Hours)"
elif weight_metric == "risk":
    metric_label = "Cumulative Risk Score"
elif dataset_choice == "Dubai Humanitarian Network":
    metric_label = "Transport Cost (USD/tonne)"
else:
    metric_label = "Transport Cost (Simulated Units)"

algorithm_choice = st.sidebar.selectbox(
    "Algorithm Selection",
    ["Compare Both", "Dijkstra's Algorithm", "A* Search"]
)


def get_disrupted_graph(original_graph, blocked_list):
    mod_graph = copy.deepcopy(original_graph)
    for block in blocked_list:
        loc_a, loc_b = block.split(" <-> ")
        if loc_a in mod_graph:
            mod_graph[loc_a] = [r for r in mod_graph[loc_a] if r["destination"] != loc_b]
        if loc_b in mod_graph:
            mod_graph[loc_b] = [r for r in mod_graph[loc_b] if r["destination"] != loc_a]
    return mod_graph


st.sidebar.markdown("---")
st.sidebar.header("Disruption Controls")

if dataset_choice == "Synthetic Network":
    # Synthetic routes are bidirectional.
    all_edges = []
    for loc, routes in graph.items():
        for route in routes:
            edge = tuple(sorted([loc, route["destination"]]))
            if edge not in all_edges:
                all_edges.append(edge)

    blocked_edges = st.sidebar.multiselect(
        "Disable Routes",
        [f"{a} <-> {b}" for a, b in all_edges]
    )
    active_graph = get_disrupted_graph(graph, blocked_edges)
    disruption_count = len(blocked_edges)
    disruption_metric_label = "Active Disruptions"
    disruption_metric_value = disruption_count
else:
    # Representative disruptions use directed leg IDs via evaluation.py.
    scenario_id = st.sidebar.selectbox(
        "Disruption Scenario",
        [f"S{i}" for i in range(10)]
    )
    active_graph = apply_hrp_scenario(graph, scenario_id)
    disruption_count = 0 if scenario_id == "S0" else 1
    disruption_metric_label = "Selected Scenario"
    disruption_metric_value = scenario_id

# Top Metrics Bar
col_a, col_b, col_c = st.columns(3)
col_a.metric("Origin Hub", format_location(start_node))
col_b.metric("Selected Destination", format_location(goal_node))
col_c.metric(disruption_metric_label, disruption_metric_value)

st.markdown("---")

# Compute Route Button
if st.button("Compute Optimal Route", type="primary"):
    col1, col2 = st.columns(2)

    def run_algorithm(name, func):
        if func is None:
            st.warning(f"Module for {name} is not available yet.")
            return

        path, total_weight, nodes_explored = func(active_graph, start_node, goal_node, weight_metric)

        if not path or total_weight == float("inf"):
            st.error(f"{name}: Destination unreachable.")
        else:
            st.success(f"{name} Completed")
            readable_path = [format_location(node) for node in path]
            st.write(f"**Route Path:** {' → '.join(readable_path)}")

            m1, m2 = st.columns(2)
            m1.metric(metric_label, f"{total_weight:.2f}")
            m2.metric("Nodes Explored", nodes_explored)

            try:
                totals = calculate_route_totals(active_graph, path, weight_metric)
                if isinstance(totals, dict):
                    t_cols = st.columns(len(totals))
                    for idx, (k, v) in enumerate(totals.items()):
                        if isinstance(v, (int, float)):
                            t_cols[idx].metric(str(k).replace("_", " ").title(), f"{v:.2f}")
                        else:
                            t_cols[idx].metric(str(k).replace("_", " ").title(), str(v))
            except Exception:
                pass

    with col1:
        st.subheader("Dijkstra's Results")
        if algorithm_choice in ["Compare Both", "Dijkstra's Algorithm"]:
            run_algorithm("Dijkstra", dijkstra_search)
        else:
            st.info("Dijkstra execution skipped.")

    with col2:
        st.subheader("A* Search Results")
        if algorithm_choice in ["Compare Both", "A* Search"]:
            run_algorithm("A*", astar_search)
        else:
            st.info("A* execution skipped.")

st.markdown("---")

with st.expander("Developer Debug: View Active Network Adjacency JSON"):
    st.json(active_graph)
