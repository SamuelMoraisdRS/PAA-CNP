"""
Undirected graph implementation using the adjacency list model.
Instances must be created from a text source file following the
Ventresca format.
"""


class Graph:
    def __init__(self, filepath: str):
        with open(filepath, "r") as f:
            lines = f.readlines()

        # Number of vertices
        n_vertices = int(lines[0].strip())

        # empty adj list
        adj_list = [[] for _ in range(n_vertices)]

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            vertice, neighbours = line.split(":")
            vertice = int(vertice.strip())
            neighbours = [int(v) for v in neighbours.split() if v]
            adj_list[vertice] = neighbours

        self.adj_list = adj_list

    def num_vertices(self) -> int:
        return len(self.adj_list)
