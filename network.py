"""Transport network for the CSCI218 Humanitarian Route Planner.

This module will load our simulated route dataset
and prepare it for Dijkstra and A* search.
"""
import csv

def load_network():
    """
    Creates a graph to store locations and their transport routes.
    The graph will be used by Dijkstra and A* to find the best route.
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

    return graph
