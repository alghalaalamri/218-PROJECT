
"""Dijkstra's shortest-path algorithm for the Humanitarian Route Planner."""

import heapq


def dijkstra_search(graph, start, goal, weight="time"):
    """
    Find the shortest-time or lowest-cost route using Dijkstra.

    Returns:
        path: List of locations in the selected route
        total_weight: Total time or cost of the route
        nodes_explored: Number of nodes explored
    """

    # Check whether the selected weight is valid.
    if weight not in ("time", "cost"):
        raise ValueError("Weight must be 'time' or 'cost'.")

    # Check whether the start and destination exist.
    if start not in graph or goal not in graph:
        return [], float("inf"), 0

    # Priority queue: (total weight, current node)
    priority_queue = [(0, start)]

    # Store the best known weight to each location.
    distances = {node: float("inf") for node in graph}
    distances[start] = 0

    # Store previous nodes to reconstruct the route.
    previous = {}

    # Track visited nodes.
    visited = set()
    nodes_explored = 0

    while priority_queue:
        current_weight, current_node = heapq.heappop(priority_queue)

        # Skip nodes already explored.
        if current_node in visited:
            continue

        visited.add(current_node)
        nodes_explored += 1

        # Stop when the destination is reached.
        if current_node == goal:
            break

        # Check all connections from the current location.
        for edge in graph[current_node]:
            neighbor = edge["destination"]
            edge_weight = edge[weight]

            # Dijkstra requires non-negative edge weights.
            if edge_weight < 0:
                raise ValueError("Negative route weights are not supported.")

            if neighbor in visited:
                continue

            # Calculate the new total weight.
            new_weight = current_weight + edge_weight

            # Update the route if a better path is found.
            if new_weight < distances[neighbor]:
                distances[neighbor] = new_weight
                previous[neighbor] = current_node

                heapq.heappush(
                    priority_queue,
                    (new_weight, neighbor)
                )

    # Handle unreachable destinations.
    if goal not in visited:
        return [], float("inf"), nodes_explored

    # Reconstruct the shortest route.
    path = []
    current_node = goal

    while current_node != start:
        path.append(current_node)
        current_node = previous[current_node]

    path.append(start)
    path.reverse()

    return path, distances[goal], nodes_explored

