import streamlit as st
import copy
from network import load_network

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
st.write("Interactive pathfinding and infrastructure disruption simulator for emergency relief logistics[cite: 1, 2].")

# Load graph network
graph = load_network()
locations = list(graph.keys())

# Sidebar Configuration
st.sidebar.header("Route Parameters")

start_node = "Dubai"
goal_node = st.sidebar.selectbox("Select Crisis Destination", [loc for loc in locations if loc != start_node])

weight_metric = st.sidebar.selectbox("Optimization Goal", ["time", "cost"])
metric_label = "Travel Time (Hours)" if weight_metric == "time" else "Transport Cost (Units)"

algorithm_choice = st.sidebar.selectbox("Algorithm Selection", ["Compare Both", "Dijkstra's Algorithm", "A* Search"])

st.sidebar.markdown("---")
st.sidebar.header("Disruption Controls")

# Extract unique edges for the multi-select box
all_edges = []
for loc, routes in graph.items():
    for r in routes:
        edge = tuple(sorted([loc, r["destination"]]))
        if edge not in all_edges:
            all_edges.append(edge)

blocked_edges = st.sidebar.multiselect(
    "Disable Routes", 
    [f"{edge[0]} <-> {edge[1]}" for edge in all_edges]
)

def get_disrupted_graph(original_graph, blocked_list):
    mod_graph = copy.deepcopy(original_graph)
    for block in blocked_list:
        locA, locB = block.split(" <-> ")
        if locA in mod_graph:
            mod_graph[locA] = [r for r in mod_graph[locA] if r["destination"] != locB]
        if locB in mod_graph:
            mod_graph[locB] = [r for r in mod_graph[locB] if r["destination"] != locA]
    return mod_graph

active_graph = get_disrupted_graph(graph, blocked_edges)

# Top Metrics Bar
col_a, col_b, col_c = st.columns(3)
col_a.metric("Origin Hub", start_node)
col_b.metric("Selected Destination", goal_node)
col_c.metric("Active Disruptions", len(blocked_edges))

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
            st.write(f"**Route Path:** {' ➔ '.join(path)}")
            
            m1, m2 = st.columns(2)
            m1.metric(metric_label, f"{total_weight:.1f}")
            m2.metric("Nodes Explored", nodes_explored)

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

# Clean hidden expander for developer view
with st.expander("Developer Debug: View Network Adjacency JSON"):
    st.json(active_graph)
