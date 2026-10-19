"""
Implementação de classe para grafos não direcionados utilizando lista de adjacência.
Os objetos são instanciados a partir de documentos .txt no formato proposto por Ventresca
"""

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

            # NOTE : existem arestas paralelas em alguns vertices (duas arestas conectando os mesmos dois vertices).
            # Para este problema, essas arestas nao sao relevantes, pois queremos apenas saber a conexao entre os nos,
            # entao vamos ignora-las removendo os valores duplicados nas listas de adjacencia
            adj_list[vertice] = list(dict.fromkeys(neighbour_list))

        self.adj_list = adj_list

    @classmethod
    def from_adj_list(cls, adj_list: list[list[int]]) -> "Graph":
        graph = cls.__new__(cls)
        graph.adj_list = adj_list
        return graph

    def num_vertices(self) -> int:
        return len(self.adj_list)

    def num_edges(self) -> int:
        return sum(len(neigh) for neigh in self.adj_list) // 2
