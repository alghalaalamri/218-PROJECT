"""Dijkstra shortest-path algorithm for a directed or undirected adjacency-list graph.

Each edge needs destination and non-negative time/cost values. Additional fields
(leg_id, risk, etc.) are ignored by the shortest-path search itself.
"""
import heapq


def dijkstra_search(graph, start, goal, weight="time"):
    """Return (path, total_weight, nodes_explored) for one selected edge weight.

    nodes_explored counts unique nodes removed from the queue for processing.
    """
    if weight not in ("time", "cost", "risk"):
        raise ValueError("weight must be 'time', 'cost', or 'risk'")
    if start not in graph or goal not in graph:
        return [], float("inf"), 0

    distances = {node: float("inf") for node in graph}
    previous = {}
    distances[start] = 0.0
    priority_queue = [(0.0, start)]
    visited = set()
    nodes_explored = 0

    while priority_queue:
        current_weight, current_node = heapq.heappop(priority_queue)
        if current_node in visited:
            continue
        visited.add(current_node)
        nodes_explored += 1
        if current_node == goal:
            break

        for edge in graph[current_node]:
            edge_weight = float(edge[weight])
            if edge_weight < 0:
                raise ValueError("Dijkstra cannot use negative edge weights")
            neighbor = edge["destination"]
            if neighbor in visited:
                continue
            candidate = current_weight + edge_weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (candidate, neighbor))

    if goal not in visited:
        return [], float("inf"), nodes_explored
    path = []
    node = goal
    while node != start:
        path.append(node)
        node = previous[node]
    path.append(start)
    path.reverse()
    return path, distances[goal], nodes_explored
