'''Class for the graph. It is a barebones graph that really just
creates a distance table that functions as an adjacency matrix
with distances used as weights.'''


class Graph:
    def __init__(self):
        '''Initializes the graph'''
        self.distance_list = {}
        self.total_distance = 0

    def add_map_edge(self, location_a, location_b, distance):
        '''Creates a "map edge" from imported CSV data. The original
        data only provides the distance from a to b, so this
        function creates an undirected edge by copying the
        distance from a to b onto b to a.'''
        self.distance_list[(location_a, location_b)] = distance
        self.distance_list[(location_b, location_a)] = distance

    def get_distance(self, location_a, location_b):
        '''Gets the direct distance between any two points.'''
        return self.distance_list.get((location_a, location_b))
