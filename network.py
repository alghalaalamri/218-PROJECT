"""Transport network for the CSCI218 Humanitarian Route Planner.

This module will load our simulated route dataset
and prepare it for Dijkstra and A* search.
"""
import csv

def load_network():
    """
    Loads transport routes from the CSV file into a graph.
    Each connection is bidirectional and stores its transport
    type, travel time, and cost for Dijkstra and A*.
    """
    file_path = "data/routes.csv"
    graph = {}

    # Open the CSV file and prepare its rows for reading.
    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        # Go through each transport route in the CSV.
        for row in reader:
            # Extract the details of each transport connection.
            start = row["from_location"]
            destination = row["to_location"]
            transport = row["transport_type"]

            # Convert travel time and cost from text into numbers.
            time = float(row["travel_time_hours"])
            cost = float(row["transport_cost"])

            # Make sure both locations exist in the graph.
            if start not in graph:
                graph[start] = []

            if destination not in graph:
                graph[destination] = []

            # Add the forward connection.
            graph[start].append({
                "destination": destination,
                "transport": transport,
                "time": time,
                "cost": cost
            })

            # Add the reverse connection with the same values.
            graph[destination].append({
                "destination": start,
                "transport": transport,
                "time": time,
                "cost": cost
            })

    return graph
