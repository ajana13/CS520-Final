import osmnx as ox
import networkx as nx
from collections import defaultdict, deque
from heapq import heapify, heappush, heappop
import pandas as pd
import utils

class Search:

    def __init__(self, Graph, x=0.0, elevation_type="maximize"):
        self.Graph = Graph
        self.x = x
        self.elevation_type = elevation_type
        self.start_node = None
        self.end_node = None
        self.best = [[], 0.0, float('-inf'), 0.0]
        self.shortest_dist = None
    
    def reset_graph(self, new_graph):
        self.Graph = new_graph

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
        elevation_dist, drop_distance = utils.get_elevation(route, "elevation_gain"), utils.get_elevation(route, "elevation_drop")
        self.best = [route[:], cost, elevation_dist, drop_distance]       


# graph = pd.read_pickle('../Model/map.p')

# s = [42.3868, -72.5301]
# e = [42.22560, -72.31122]
# graph = g.get_graph(s,e)
# a = Search(graph)
# a.dijkstra()
# print(a.best) 
