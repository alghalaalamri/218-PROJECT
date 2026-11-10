# Humanitarian Route Planner

CSCI218 - Foundations of Artificial Intelligence
University of Wollongong in Dubai | Autumn 2026

## Project Overview
A Python-based humanitarian logistics route planner that compares Dijkstra's algorithm and A* search to identify efficient routes from Dubai to a simulated crisis destination.

## Team Components
- Network and dataset: Alghala
- Dijkstra's algorithm: Alina
- A* search: Jawaher
- Interactive interface: Iqra
- Evaluation and testing: Abdelali

## Status
Project under development.


----------------------
## Network and Dataset Guide

*For team members working on Dijkstra, A\*, evaluation, and the user interface.*

The transport network is stored in `data/routes.csv` and loaded using `load_network()` from `network.py`.

The dataset contains **8 locations and 12 simulated bidirectional routes** (24 directed connections). Travel times and costs are hypothetical and do not represent verified operational transport corridors.

### 1. Loading the Network

```python
from network import load_network

graph = load_network()
```

### 2. Graph Structure

The network uses an adjacency-list dictionary. Each location contains a list of connected routes.

Example:

```python
{
    "Dubai": [
        {
            "destination": "Abu Dhabi",
            "transport": "road",
            "time": 2.0,
            "cost": 100.0
        }
    ]
}
```

Each route contains:

- `destination`: Connected location
- `transport`: Road, air, or sea
- `time`: Travel time in hours
- `cost`: Simulated transport cost units

To access connections:

```python
for route in graph["Dubai"]:
    destination = route["destination"]
    travel_time = route["time"]
    transport_cost = route["cost"]
```

### 3. Team Integration Guidelines

**Algorithm inputs**

Both Dijkstra and A* should accept:

```python
(graph, start, goal, weight)
```

- `graph`: Network returned by `load_network()`
- `start` / `goal`: Location names from the CSV
- `weight`: `"time"` or `"cost"`

**Algorithm outputs**

Both algorithms should return:

```python
(path, total_weight, nodes_explored)
```

- `path`: List of locations in the selected route
- `total_weight`: Total value of the selected optimization weight
- `nodes_explored`: Number of unique locations processed during the search

If no route exists, return:

```python
([], float("inf"), nodes_explored)
```

**Blocked routes**

The interface should remove blocked connections in both directions from a copy of the graph before running either algorithm. The original network remains unchanged.

**Evaluation**

Both algorithms should use the same network, optimization weight, and disruption scenarios for fair comparisons.

**A* heuristic**

The A* implementation should use and justify an appropriate heuristic that does not overestimate the remaining weight if optimality is claimed.
Pathfinding algorithms, route disruptions, and the user interface
are implemented separately.
