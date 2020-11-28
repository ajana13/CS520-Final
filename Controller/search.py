import osmnx as ox
import networkx as nx
import time
from collections import defaultdict, deque
from heapq import heapify, heappush, heappop
# import pandas as pd

class Search:

    def __init__(self, Graph, x=0.0, elevation_type="maximize"):
        self.Graph = Graph
        self.x = x
        self.elevation_type = elevation_type
        self.start_node = None
        self.end_node = None
        self.best = [[], 0.0, float('-inf'), 0.0]
    
    def reset_graph(self, new_graph):
        self.Graph = new_graph
    
    def get_cost(self, node_a, node_b, cost_type = "normal"):

        def cost_normal():
            try : 
                return Graph.edges[node_a, node_b ,0]["length"]
            except : 
                return Graph.edges[node_a, node_b]["weight"]
        
        def cost_diff():
            return Graph.nodes[node_b]["elevation"] - Graph.nodes[node_a]["elevation"]
        
        def cost_gain():
            return max(0.0, Graph.nodes[node_b]["elevation"] - Graph.nodes[node_a]["elevation"])
        
        def cost_drop():
            return max(0.0, Graph.nodes[node_a]["elevation"] - Graph.nodes[node_b]["elevation"])
        
        def cost_default():
            return abs(Graph.nodes[node_a]["elevation"] - Graph.nodes[node_b]["elevation"])

        Graph = self.Graph
        if node_a is None or node_b is None : 
            return 
            
        switcher = {
            "normal": cost_normal(),
            "elevation_diff": cost_diff(),
            "elevation_gain": cost_gain(),
            "elevation_drop" : cost_drop()
        }
        return abs(Graph.nodes[node_a]["elevation"] - Graph.nodes[node_b]["elevation"])


    def get_elevation(self, route, cost_type = "both", is_total = False):

        def val_elev_normal():
            return self.get_cost(route[i], route[i+1], "normal")

        def val_elev_diff():
            return self.get_cost(route[i], route[i+1], "elevation_difference")
    
        def val_elev_gain():
            return self.get_cost(route[i], route[i+1], "elevation_gain")

        def val_elev_drop():
            return self.get_cost(route[i], route[i+1], "elevation_drop")

        total_elev = 0
        if not is_total:
            piece_elevation = []
        for i in range(len(route)-1):
            diff = 0
            switcher = {
                "normal": val_elev_normal(),
                "elevation_drop": val_elev_drop(),
                "elevation_gain": val_elev_gain(),
                "both" : val_elev_diff()
            }
            diff = switcher.get(cost_type, lambda: 0)
            total_elev += diff
            if not is_total:
                piece_elevation.append(diff)
        if not is_total:
            return total_elev, piece_elevation
        else:
            return total_elev
    

    def get_route(self, parent_node, end):
        
        path = [end]
        curr = parent_node[end]
        while curr!=-1:
            path.append(curr)
            curr = parent_node[curr]
        return path[::-1]

    def end_seach(self):
        return not (self.start_node == None or self.end_node == None)

    def found_end(self, parent_node, cost):
        route = self.get_route(parent_node, self.end_node)
        elevation_dist, drop_distance = self.get_elevation(route, "elevation_gain"), self.get_elevation(route, "elevation_drop")
        self.best = [route[:], cost, elevation_dist, drop_distance]

    def get_shortest_distance(self, start_point, end_point, x, elevation_type = "minimize"):

        Graph = self.Graph
        self.x  = x/100
        self.elevation_type = elevation_type
        self.start_node = None
        self.end_node = None

        self.start_node, distance1 = ox.get_nearest_node(Graph, point=self.start_point, return_dist = True)
        self.end_node, distance2 = ox.get_nearest_node(Graph, point=self.end_point, return_dist = True)

        self.shortest_route = nx.shortest_path(Graph, source = self.start_node, target = self.end_node, weight = 'length')
        self.shortest_dist  = sum(ox.get_route_edge_attributes(G, self.shortest_route, 'length'))
        
        self.shortest_latitude_longitude = [[Graph.nodes[node]['x'],Graph.nodes[node]['y']] for node in self.shortest_route] 
        
        self.shortest_path_data = [shortest_latitude_longitude, self.shortest_dist, \
                            self.get_elevation(self.shortest_route, "elevation_gain"), self.get_elevation(self.shortest_route, "elevation_drop")]

        if(x == 0):
            return shortest_path_data, shortest_path_data
        
        set_best_path(elevation_type)

        start = time.time()
        self.dijkstra
        end = time.time()
        dijkstra_path = self.best

        set_best_path(elevation_type)
        
        start = time.time()
        self.a_star()
        end = time.time()
        a_star_path = self.best

        if self.elevation_type == "minimize": 
            self.best = get_best_minimize(dijkstra_path, a_star_path) 
        else: 
            self.best = get_best_maximize(dijkstra_path, a_star_path)
        
        if (self.elevation_type == "minimize"):
            min = True if self.best[3] == float('-inf') else False
        else: 
            max = True if self.best[2] == float('-inf') else False
        
        if min or max: return shortest_path_data, [[], 0.0, 0, 0]

        self.best[0] = [[Graph.nodes[node]['x'],Graph.nodes[node]['y']] for node in self.best[0]]

        if (self.elevation_type == "minimize"):
            min = True if self.best[2] > shortest_path_data[2] else False
        else: 
            min = True if self.best[2] < shortest_path_data[2] else False
        
        if min or max: self.best = shortest_path_data

        return shortest_path_data, self.best

    
    def set_best_path(self, elevation_type):
        if elevation_type == "minimize": 
            self.best = [[], 0.0, float('inf'), float('-inf')]
        else:
            self.best = [[], 0.0, float('-inf'), float('-inf')]
    
    def get_best_maximize(self, dijkstra_path, a_star_path):
        return a_star_path if (dijkstra_path[2] != a_star_path[2] or dijkstra_path[1] > a_star_path[1]) and (dijkstra_path[2] < a_star_path[2]) else dijkstra_path
        
    def get_best_minimize(self, dijkstra_path, a_star_path):
        return a_star_path if (dijkstra_path[2] != a_star_path[2] or dijkstra_path[1] > a_star_path[1]) and (dijkstra_path[2] > a_star_path[2]) else dijkstra_path
       


# graph = pd.read_pickle('../Model/map.p')
# s = [42.3868, -72.5301]
# e = [42.22560, -72.31122]
# graph = g.get_graph(s,e)
# a = Search(graph)
# a.dijkstra()
# print(a.best) 
