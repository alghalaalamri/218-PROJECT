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

*For team members working on Dijkstra, A*, evaluation, and the user interface.*

The project uses two transport datasets: an original simulated network and a representative humanitarian network provided through the course. Both are loaded through `network.py` and use a compatible adjacency-list structure for the routing algorithms.

### 1. Datasets

**Original Simulated Network — `routes.csv`**

- 8 locations and 12 simulated bidirectional routes (24 directed connections).
- Includes road, air, and sea transport.
- Contains travel time in hours and transport cost in simulated units.
- Routes and values are hypothetical and do not represent verified operational transport corridors.

**Representative Humanitarian Network**

- `locations.csv`: Information about 23 locations, including their identifiers, names, types, and countries.
- `network_legs.csv`: 36 directed transport legs containing travel time, cost, risk, capacity, reliability, and other attributes.
- `hrp_disruption_scenarios.csv`: Baseline and disruption scenarios affecting transport connections.

The representative dataset uses typical transit hours, transport cost in USD per tonne, and risk scores from 1 to 5. Unlike the original network, its connections are directed and are not automatically reversible.

The datasets represent different transport networks and destinations. They are evaluated separately rather than treated as equivalent delivery journeys.

### 2. Loading the Networks

**Original simulated network:**

```python
from network import load_network

graph = load_network()
```

**Representative network:**

```python
from network import load_representative_network

graph, locations = load_representative_network()
```

The representative loader returns:

- `graph`: Adjacency-list dictionary used by the routing algorithms.
- `locations`: Dictionary containing location names, types, and countries, indexed by node ID.

The original network uses location names such as `"Dubai"`, while the representative network uses node IDs such as `"IHC"`.

### 3. Graph Structure

Both networks use an adjacency-list dictionary. Each location contains a list of outgoing connections.

Example from the original simulated network:

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

Each connection contains:

- `destination`: Connected location or destination node ID.
- `transport`: Road, air, sea, or another transport mode specified in the dataset.
- `time`: Travel time in hours.
- `cost`: Transport cost, using the units of the selected dataset.

The representative network also includes:

- `risk`: Route risk score.
- `leg_id`: Unique identifier for the transport leg.
- `time_p90`: 90th-percentile transit time.
- `distance_km`: Transport distance in kilometres.
- `capacity`: Weekly transport capacity in tonnes.
- `reliability`: Reliability percentage.

To access connections:

```python
for route in graph["Dubai"]:
    destination = route["destination"]
    travel_time = route["time"]
    transport_cost = route["cost"]
```

For the representative network, use its node IDs instead, such as `graph["IHC"]`.

### 4. Team Integration Guidelines

**Algorithm inputs**

Both Dijkstra and A* should accept:

```python
(graph, start, goal, weight)
```

- `graph`: Network returned by the selected loader.
- `start` / `goal`: Valid location names or node IDs from that network.
- `weight`: `"time"` or `"cost"` for both networks; `"risk"` is additionally available for the representative network.

**Algorithm outputs**

Both algorithms should return:

```python
(path, total_weight, nodes_explored)
```

- `path`: List of locations or node IDs in the selected route.
- `total_weight`: Total value of the selected optimization weight.
- `nodes_explored`: Number of unique locations processed during the search.

If no route exists, return:

```python
([], float("inf"), nodes_explored)
```

**Blocked routes and disruptions**

The interface should apply route changes to a copy of the graph so the original network remains unchanged.

- For the original simulated network, blocked routes should be removed in both directions.
- For the representative network, disruptions should target the specified `leg_id` values. The provided scenarios include route removals and travel-time or cost multipliers.

The disruption scenario CSV is included in the repository, but applying its scenarios requires separate implementation.

**Evaluation**

Both algorithms should be evaluated using the same dataset, start and destination, optimization weight, and disruption conditions for each comparison.

The representative network supports additional evaluation scenarios using the supplied disruption definitions. Results should include the selected route, total travel time, total transport cost, and nodes explored where available.

Because the datasets use different routes, destinations, and cost units, their numerical results should not be directly compared as equivalent journeys.

**A* heuristic**

The A* implementation should use and justify an appropriate heuristic that does not overestimate the remaining weight if optimality is claimed.

### 5. Validation and Implementation Notes

Both network loaders were tested in Google Colab by Alghala.

- The simulated network loaded 8 locations and 24 directed connections.
- The representative network loaded 23 locations and 36 directed connections.
- Representative transport legs were checked for unique identifiers, valid destinations, and non-negative time, cost, and risk values.

