"""
test_routes.py - Automated Unit, Optimality, and Admissibility Tests

"""

import unittest
from network import load_network
from dijkstra import dijkstra_search
from astar import astar_search, heuristic_scale, haversine_km
from evaluation import create_disrupted_network


class TestHumanitarianRouting(unittest.TestCase):

    def setUp(self):
        self.graph = load_network()

    def test_network_topology(self):
        """Verifies exact 8 hubs and 24 directed edges (12 bidirectional routes)."""
        self.assertEqual(len(self.graph), 8)
        directed_edges = sum(len(edges) for edges in self.graph.values())
        self.assertEqual(directed_edges, 24)

    def test_heuristic_admissibility(self):
        """Verifies h(n) never overestimates actual edge weights across the graph."""
        for weight in ("time", "cost"):
            scale = heuristic_scale(self.graph, weight)
            self.assertIsNotNone(scale)
            for u, edges in self.graph.items():
                for edge in edges:
                    v = edge["destination"]
                    h_est = haversine_km(u, v) * scale
                    self.assertLessEqual(h_est, edge[weight] + 1e-9)

    def test_all_pairs_optimality_match(self):
        """Dijkstra and A* must return identical optimal weights for every node pair."""
        for u in self.graph:
            for v in self.graph:
                if u == v:
                    continue
                for weight in ("time", "cost"):
                    _, d_weight, _ = dijkstra_search(self.graph, u, v, weight)
                    _, a_weight, _ = astar_search(self.graph, u, v, weight)
                    self.assertAlmostEqual(d_weight, a_weight, places=5)

    def test_airspace_closure_reroute(self):
        """Closing all 3 air corridors forces rerouting through Abu Dhabi and Jeddah."""
        blocked = [("Dubai", "Amman"), ("Dubai", "Riyadh"), ("Riyadh", "Amman")]
        disrupted = create_disrupted_network(self.graph, blocked)

        d_path, d_weight, _ = dijkstra_search(disrupted, "Dubai", "Gaza", "time")
        a_path, a_weight, _ = astar_search(disrupted, "Dubai", "Gaza", "time")

        expected_path = ["Dubai", "Abu Dhabi", "Riyadh", "Jeddah", "Al Arish", "Gaza"]
        self.assertEqual(d_path, expected_path)
        self.assertEqual(a_path, expected_path)
        self.assertEqual(d_weight, 42.0)
        self.assertEqual(a_weight, 42.0)

    def test_unreachable_chokepoint(self):
        """Severing Al Arish <-> Gaza isolates Gaza and returns ([], inf, nodes)."""
        disrupted = create_disrupted_network(self.graph, [("Al Arish", "Gaza")])
        for search_fn in (dijkstra_search, astar_search):
            path, weight, nodes = search_fn(disrupted, "Dubai", "Gaza", "time")
            self.assertEqual(path, [])
            self.assertEqual(weight, float("inf"))
            self.assertEqual(nodes, 7)


if __name__ == "__main__":
    unittest.main()