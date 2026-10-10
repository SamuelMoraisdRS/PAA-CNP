"""
Undirected graph implementation using the adjacency list model.
Instances must be created from a text source file following the
Ventresca format.
"""

# Allows annotations like list[int] on Python < 3.9
from __future__ import annotations


class Graph:
    def __init__(self, filepath: str):
        with open(filepath, "r") as f:
            lines = f.readlines()

        n_vertices = int(lines[0].strip())
        adj_list = [[] for _ in range(n_vertices)]

        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            vertice, neighbours = line.split(":")
            vertice = int(vertice.strip())
            neighbour_list = [int(v) for v in neighbours.split() if v]
            # Some instances list the same neighbour twice (parallel edges);
            # keep each neighbour once, preserving the original order
            adj_list[vertice] = list(dict.fromkeys(neighbour_list))

        self.adj_list = adj_list

    @classmethod
    def from_adj_list(cls, adj_list: list[list[int]]) -> "Graph":
        """Builds a graph directly from an adjacency list (used by tests)."""
        graph = cls.__new__(cls)
        graph.adj_list = adj_list
        return graph

    def num_vertices(self) -> int:
        return len(self.adj_list)

    def num_edges(self) -> int:
        return sum(len(neigh) for neigh in self.adj_list) // 2
