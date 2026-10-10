"""
'greedy2' algorithm (Addis et al.) with the fast evaluation proposed by
Ventresca & Aleman (2015).

Instead of recomputing f from scratch for every candidate, a single
iterative DFS over the residual graph computes f(G \\ (S U {v})) for ALL
vertices v at once, using articulation point information (Tarjan's dfn/low
values) and DFS subtree sizes. Each iteration costs O(n+m) and the whole
algorithm O(k(n+m)).
"""

# Allows annotations like set[int] and int | None on Python < 3.10
from __future__ import annotations

from graph import Graph

from f_function import pairs

import math


def evaluate_all(graph: Graph, removed: set[int]) -> list[int | None]:
    """
    Returns a list where position v holds f(G \\ (removed U {v})) for every
    vertex v not in 'removed' (and None for the removed vertices).
    """
    n = graph.num_vertices()
    adj = graph.adj_list

    is_removed = [False] * n
    for v in removed:
        is_removed[v] = True

    dfn = [-1] * n          # DFS visiting order (-1 = not visited yet)
    low = [0] * n           # lowest dfn reachable from v's subtree with one back edge
    subtree_size = [1] * n  # vertices in v's DFS subtree (v included)
    parent = [-1] * n
    next_neigh = [0] * n    # next position of adj[v] to explore (explicit stack)
    cut_mass = [0] * n      # vertices cut off from the component if v is removed
    split_value = [0] * n   # sum of pairs() over the subtrees cut off by v

    result = [None] * n
    total_f = 0
    counter = 0

    for root in range(n):
        if is_removed[root] or dfn[root] != -1:
            continue

        # Iterative DFS over the component of 'root' (no recursion: graphs
        # with thousands of vertices would overflow Python's call stack)
        dfn[root] = low[root] = counter
        counter += 1
        component = [root]
        stack = [root]
        while stack:
            v = stack[-1]
            if next_neigh[v] < len(adj[v]):
                w = adj[v][next_neigh[v]]
                next_neigh[v] += 1
                if is_removed[w] or w == parent[v]:
                    continue
                if dfn[w] == -1:
                    # Tree edge: go down to w
                    parent[w] = v
                    dfn[w] = low[w] = counter
                    counter += 1
                    component.append(w)
                    stack.append(w)
                else:
                    # Back edge: uses dfn[w], not low[w]
                    low[v] = min(low[v], dfn[w])
            else:
                # Every neighbour of v explored: v's subtree is complete,
                # so its values can be passed up to the parent
                stack.pop()
                p = parent[v]
                if p != -1:
                    low[p] = min(low[p], low[v])
                    subtree_size[p] += subtree_size[v]
                    if low[v] >= dfn[p]:
                        # Cut child: no back edge from v's subtree escapes
                        # above p, so removing p isolates this subtree
                        cut_mass[p] += subtree_size[v]
                        split_value[p] += pairs(subtree_size[v])

        comp_size = len(component)
        comp_pairs = pairs(comp_size)
        total_f += comp_pairs
        for v in component:
            # Ancestors and non-cut subtrees stay together as one piece
            remainder = comp_size - 1 - cut_mass[v]
            # Change in f caused by removing v (total_f is added below,
            # once every component has been visited)
            result[v] = split_value[v] + pairs(remainder) - comp_pairs

    for v in range(n):
        if result[v] is not None:
            result[v] += total_f

    return result


def greedy2_dfs(graph: Graph, k: int) -> tuple[list[int], list[int]]:
    """
    Same output as greedy2: the removed vertices in the order they were
    chosen and the value of f(G \\ S) after each iteration.
    """
    S = set()
    order = []
    history = []
    k = min(k, graph.num_vertices())
    while len(S) < k:
        values = evaluate_all(graph, S)
        critical_node = None
        lowest_f_value = math.inf
        # Same tie-breaking as greedy2: the lowest index wins
        for i in range(graph.num_vertices()):
            if values[i] is not None and values[i] < lowest_f_value:
                lowest_f_value = values[i]
                critical_node = i

        S.add(critical_node)
        order.append(critical_node)
        history.append(lowest_f_value)
        if lowest_f_value == 0:
            break

    return order, history
