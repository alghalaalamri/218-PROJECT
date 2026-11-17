"""
Heuristic: h(n) = straight line (haversine) km from n to the goal, multiplied by the
smallest weight-per-km found on any edge. This never overestimates the true remaining
weight (admissible) and satisfies h(u) <= w(u, v) + h(v) (consistent), so A* returns
an optimal route and each location only needs to be explored once.
"""
import heapq
import math
# These are the approximate (latitude, longitude) of each location used by the heuristic.
COORDINATES = {
    "Dubai": (25.2048, 55.2708),
    "Abu Dhabi": (24.4539, 54.3773),
    "Riyadh": (24.7136, 46.6753),
    "Jeddah": (21.4858, 39.1925),
    "Amman": (31.9454, 35.9284),
    "Aqaba": (29.5320, 35.0063),
    "Al Arish": (31.1316, 33.7984),
    "Gaza": (31.5017, 34.4668),
    "DWC": (24.896, 55.161),
    "DXB": (25.253, 55.365),
    "IHC": (24.985, 55.090),
    "JEA": (25.011, 55.061),
    "JED_AIR": (21.680, 39.157),
    "JED_PORT": (21.480, 39.170),
    "DJI_AIR": (11.547, 43.159),
    "DJI_PORT": (11.600, 43.090),
    "ADD": (8.978, 38.799),
    "ASW": (24.089, 32.899),
    "CAI": (30.122, 31.406),
    "MET": (12.960, 36.150),
    "ARG": (21.990, 31.350),
    "ATB": (17.702, 33.987),
    "DGL": (19.170, 30.476),
    "EBD": (13.153, 30.233),
    "ELO": (13.183, 30.217),
    "GDF": (14.034, 35.383),
    "KSL": (15.451, 36.400),
    "KST": (13.163, 32.664),
    "OMD": (15.644, 32.478),
    "PSD_PORT": (19.590, 37.220),
    "PZU": (19.433, 37.234),
}
VALID_WEIGHTS=("time","cost")
def register_coordinates(coords):
    """Adds {name: (lat, lon)} entries so the heuristic works on a new dataset. Without coordinates, A* falls back
    to h = 0."""
    COORDINATES.update(coords)
def haversine_km(a, b):
    lat1,lon1=map(math.radians,COORDINATES[a])
    lat2,lon2=map(math.radians,COORDINATES[b])
    d_lat,d_lon=lat2-lat1,lon2-lon1
    h=math.sin(d_lat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(d_lon /2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
def heuristic_scale(graph,weight):
    ratios = []
    for u, edges in graph.items():
        for edge in edges:
            v = edge["destination"]
            if u not in COORDINATES or v not in COORDINATES:
                return None
            w = float(edge[weight])
            if w < 0:
                raise ValueError("A* cannot use negative edge weights")
            km = haversine_km(u, v)
            if km > 0:
                ratios.append(w / km)
    return min(ratios) if ratios else None
def astar_search(graph,start,goal,weight="time"):
    if weight not in VALID_WEIGHTS:
        raise ValueError("Weight must be 'time' or 'cost'.")
    if start not in graph or goal not in graph:
        return[],float("inf"),0
    scale=heuristic_scale(graph,weight)
    def h(node):
        if scale is None or node not in COORDINATES or goal not in COORDINATES:
            return 0.0
        return haversine_km(node,goal)*scale
    queue = [(h(start), h(start), start, 0.0)]
    g_score = {node: float("inf") for node in graph}.
    g_score[start] = 0.0
    previous, visited, nodes_explored = {}, set(), 0
    while queue:
        _, _, current, current_g = heapq.heappop(queue)
        if current in visited:
            continue
        visited.add(current)
        nodes_explored += 1
        if current == goal:
            break
        for edge in graph[current]:
            w = float(edge[weight])
            if w < 0:
                raise ValueError("A* cannot use negative edge weights")
            neighbor = edge["destination"]
            if neighbor in visited:
                continue
            new_g = current_g + w
            if new_g < g_score[neighbor]:
                g_score[neighbor] = new_g
                previous[neighbor] = current
                nh = h(neighbor)
                heapq.heappush(queue, (new_g + nh, nh, neighbor, new_g))
                )
    if goal not in visited:
        return [],float("inf"),nodes_explored
    # Rebuilds the route by walking back through predecessors.
    path=[]
    current_node=goal
    while current_node!=start:
        path.append(current_node)
        current_node=previous[current_node]
    path.append(start)
    path.reverse()
    return path,g_score[goal],nodes_explored
