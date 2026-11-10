
import unittest
from network import load_network

class TestNetwork(unittest.TestCase):
    """Tests that the transport network loads correctly."""

    def test_network_structure(self):
        # Load the network from the CSV file.
        graph = load_network()

        # Check that all 8 locations are included.
        self.assertEqual(len(graph), 8)

        # Check that the graph has 24 directed connections.
        total_connections = sum(len(routes) for routes in graph.values())
        self.assertEqual(total_connections, 24)

        # Check that the starting point and destination exist.
        self.assertIn("Dubai", graph)
        self.assertIn("Gaza", graph)


if __name__ == "__main__":
    unittest.main()
