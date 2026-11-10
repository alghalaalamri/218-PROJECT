import streamlit as st
import copy
from network import load_network

# Import team search algorithms if available
try:
    from dijkstra import dijkstra_search
except ImportError:
    dijkstra_search = None

try:
    from astar import astar_search
except ImportError:
    astar_search = None

st.set_page_config(page_title="Humanitarian Route Planner", layout="wide")

st.title("Dubai Humanitarian Route Planner")
st.markdown("Route optimization and disruption simulation from Dubai to regional crisis destinations[cite: 1, 2].")

# Load graph network
graph = load_network()
locations = list(graph.keys())

# Sidebar configuration
st.sidebar.header("Controls")

start_node = "Dubai"
goal_node = st.sidebar.selectbox("Crisis Destination", [loc for loc in locations if loc != start_node])

weight_metric = st.sidebar.selectbox("Optimization Metric", ["time", "cost"])
if weight_metric == "time":
    metric_label = "Travel Time (hours)"
else:
    metric_label = "Transport Cost Units"

algorithm_choice = st.sidebar.radio("Algorithm", ["Dijkstra's Algorithm", "A* Search", "Compare Both"])

st.sidebar.subheader("Disruption Simulator")
st.sidebar.markdown("Select routes to block:")

# Extract unique route edges for blocking
all_edges = []
for loc, routes in graph.items():
    for r in routes:
        edge = tuple(sorted([loc, r["destination"]]))
        if edge not in all_edges:
            all_edges.append(edge)

blocked_edges = st.sidebar.multiselect(
    "Active Blockages", 
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

# Run calculation
if st.button("Calculate Route"):
    st.markdown("---")
    st.subheader("Results")
    
    col1, col2 = st.columns(2)
    
    def run_algorithm(name, func):
        if func is None:
            st.warning(f"{name} module not loaded yet.")
            return
            
        path, total_weight, nodes_explored = func(active_graph, start_node, goal_node, weight_metric)
        
        if not path or total_weight == float("inf"):
            st.error(f"{name}: No path available to {goal_node}.")
        else:
            st.success(f"{name} Complete")
            st.write(f"**Path:** {' -> '.join(path)}")
            st.metric(label=metric_label, value=f"{total_weight:.1f}")
            st.metric(label="Nodes Explored", value=nodes_explored)

    with col1:
        st.markdown(f"### Target: {goal_node}")
        if blocked_edges:
            st.warning(f"{len(blocked_edges)} route(s) blocked.")
        else:
            st.info("No active disruptions.")
            
        if algorithm_choice in ["Dijkstra's Algorithm", "Compare Both"]:
            run_algorithm("Dijkstra's Algorithm", dijkstra_search)
            
    with col2:
        st.markdown("### Comparison")
        if algorithm_choice in ["A* Search", "Compare Both"]:
            run_algorithm("A* Search", astar_search)
        elif algorithm_choice == "Dijkstra's Algorithm":
            st.info("Select 'Compare Both' or 'A* Search' to view side-by-side metrics.")

    st.markdown("---")
    with st.expander("View Graph JSON"):
        st.json(active_graph)
