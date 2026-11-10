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
**For team members working on Dijkstra, A*, evaluation, and the user interface:**
This section explains how to load the transport network, access its connections, and retrieve travel time and cost values. Please use the documented graph structure when integrating your components.

The transport network is stored in `data/routes.csv` and loaded using
the `load_network()` function in `network.py`.

The dataset contains 8 locations and 12 simulated transport connections.
Each connection is treated as bidirectional, creating 24 directed
connections in the graph.

The routes, travel times, and costs are simulated for educational
purposes and do not represent verified operational transport corridors.

### Loading the Network

```python
from network import load_network

graph = load_network()
```

### Graph Structure

The network is represented as an adjacency-list dictionary.

Each location is a dictionary key containing a list of connections.

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

Each connection contains:

- `destination`: The connected location.
- `transport`: The transport method (road, air, or sea).
- `time`: Travel time in hours (float).
- `cost`: Simulated transport cost (float).

### Using the Network in Dijkstra and A*

Both algorithms can access a location's connections using:

```python
for route in graph["Dubai"]:
    destination = route["destination"]
    travel_time = route["time"]
    transport_cost = route["cost"]
```

The algorithms can use `time` or `cost` as the optimization weight.

The network module loads and represents the transport connections.
Pathfinding algorithms, route disruptions, and the user interface
are implemented separately.
