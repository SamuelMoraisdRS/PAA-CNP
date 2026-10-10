"""
Objective function of the Critical Node Problem (CNP).

f(G \\ S) = sum of C(|Ci|, 2) over the connected components Ci of the
residual graph obtained by removing the vertex set S from G, i.e. the
number of vertex pairs that are still connected to each other.
"""

# Allows annotations like set[int] on Python < 3.9
from __future__ import annotations

from collections import deque

from graph import Graph


def pairs(size: int) -> int:
    """C(size, 2): number of vertex pairs inside a component of this size."""
    return size * (size - 1) // 2


def f_function(graph: Graph, removed: set[int]) -> int:
    """Computes f(G \\ removed) from scratch with a BFS per component, O(n+m)."""
    n = graph.num_vertices()
    # Removed vertices are marked as visited so the BFS never enters them
    visited = [False] * n
    for v in removed:
        visited[v] = True

    total = 0
    for source in range(n):
        if visited[source]:
            continue
        visited[source] = True
        queue = deque([source])
        size = 0
        while queue:
            u = queue.popleft()
            size += 1
            for w in graph.adj_list[u]:
                if not visited[w]:
                    visited[w] = True
                    queue.append(w)
        total += pairs(size)

    return total
