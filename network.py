#Transport network for the CSCI218 Humanitarian Route Planner

import csv
from pathlib import Path


def load_network():
    """
    Loads the original simulated transport network.
    Each connection is bidirectional and stores its
    transport type, travel time, and cost.
    """

    file_path = Path(__file__).resolve().parent / "data" / "routes.csv"
    graph = {}

    with open(file_path, "r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = row["from_location"]
            destination = row["to_location"]
            transport = row["transport_type"]

            time = float(row["travel_time_hours"])
            cost = float(row["transport_cost"])

            if start not in graph:
                graph[start] = []

            if destination not in graph:
                graph[destination] = []

            graph[start].append({
                "destination": destination,
                "transport": transport,
                "time": time,
                "cost": cost
            })

            graph[destination].append({
                "destination": start,
                "transport": transport,
                "time": time,
                "cost": cost
            })

    return graph


def load_representative_network():
    """
    Loads the professor-provided representative network.

    Unlike the original network, connections are directed.
    Additional route information is preserved for evaluation
    and disruption scenarios.
    """

    data_folder = Path(__file__).resolve().parent / "data"
    locations_file = data_folder / "locations.csv"
    legs_file = data_folder / "network_legs.csv"

    graph = {}
    locations = {}

    # Load location details and create all graph nodes.
    with open(locations_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            node_id = row["node_id"]

            locations[node_id] = {
                "name": row["name"],
                "type": row["node_type"],
                "country": row["country"]
            }

            graph[node_id] = []

    # Load directed transport connections.
    with open(legs_file, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for row in reader:
            start = row["from_node"]
            destination = row["to_node"]

            # Ensure both locations exist in locations.csv.
            if start not in graph or destination not in graph:
                raise ValueError(
                    f"Unknown location in leg {row['leg_id']}"
                )

            graph[start].append({
                "destination": destination,
                "transport": row["mode"],
                "time": float(row["transit_hours_typical"]),
                "cost": float(row["cost_usd_per_tonne"]),
                "risk": float(row["risk_score_1to5"]),
                "leg_id": row["leg_id"],
                "time_p90": float(row["transit_hours_p90"]),
                "distance_km": float(row["distance_km"]),
                "capacity": float(row["capacity_tonnes_per_week"]),
                "reliability": float(row["reliability_pct"])
            })

    return graph, locations
