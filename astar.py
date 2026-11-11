import heapq
import math
COORDINATES = {
    "Dubai":(25.2048, 55.2708),
    "Abu Dhabi":(24.4539,54.3773),
    "Riyadh":(24.7136,46.6753),
    "Jeddah":(21.4858,39.1925),
    "Amman":(31.9454,35.9284),
    "Aqaba":(29.5320,35.0063),
    "Al Arish":(31.1316,33.7984),
    "Gaza":(31.5017,34.4668),
}
def haversine_km(a, b):
    lat1,lon1=map(math.radians,COORDINATES[a])
    lat2,lon2=map(math.radians,COORDINATES[b])
    d_lat,d_lon=lat2-lat1,lon2-lon1
    h=math.sin(d_lat/2)**2+math.cos(lat1)*math.cos(lat2)*math.sin(d_lon /2)**2
    return 2*6371.0088*math.asin(math.sqrt(h))
def heuristic_scale(graph,weight):
    best=None
    for node,edges in graph.items():
        for edge in edges:
            dest=edge["destination"]
            if node not in COORDINATES or dest not in COORDINATES:
                return None 
            km=haversine_km(node, dest)
            if km==0:
                continue
            per_km=edge[weight]/km
            if best is None or per_km<best:
                best=per_km
    return best 
def astar_search(graph,start,goal,weight="time"):
    if weight not in ("time","cost"):
        raise ValueError("Weight must be 'time' or 'cost'.")
    if start not in graph or goal not in graph:
        return[],float("inf"),0
    scale=heuristic_scale(graph,weight)
    def h(node):
        if scale is None or node not in COORDINATES or goal not in COORDINATES:
            return 0.0
        return haversine_km(node,goal)*scale
    start_h=h(start)
    priority_queue=[(start_h,start_h,start,0)]
    g_score={node:float("inf") for node in graph}
    g_score[start]=0
    previous={}

