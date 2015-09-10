from fetch_map import fetch_raw_map
from dijkstra import process_raw_map

class PositionState():
        
    def __init__(localMem=False, mapgraph, start, goal):
        # TODO: Implement local memory storage
        # TODO: Get all available map data, and create unified map for all levels / buildings 
        raw_map = fetch_raw_map('COM1', '2')            
        self.graph = process_raw_map(raw_map)
        self.start = start
        self.goal = goal
        

        
