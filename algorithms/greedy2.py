"""
Implementacao do 'greedy2', como proposto por Addis et al.

"""

from graph import Graph


import math


"""
Funcao de custo  'f', que deve ser minimizada pela abordagem gulosa. Retorna o numero de pares conectados em G mediante a exclusao do conjunto S de vertices.
Performa uma DFS
"""


def f_function(graph: Graph, S: set[int]):
    n = graph.num_vertices()
    visited = [False] * n
    total = 0
    for i in range(n):
        if i in S or visited[i]:
            continue
        component = []
        stack = [i]
        visited[i] = True
        while stack:
            u = stack.pop()
            component.append(u)
            for v in graph.adj_list[u]:
                if v not in S and not visited[v]:
                    visited[v] = True
                    stack.append(v)
        k = len(component)
        total += k * (k - 1) // 2
    return total


def greedy2(graph: Graph, k: int) -> set[int]:
    S = set()
    while len(S) < k:
        critical_node = 0
        curr_lowest_f_value = math.inf
        prev_f_value = math.inf
        # i = argmax (f(S) - f(S U {i}))
        for i in range(graph.num_vertices()):
            if i in S:
                continue
            curr_f_value = f_function(graph, S | {i})
            if curr_f_value < prev_f_value:
                prev_f_value = curr_f_value
                critical_node = i
        S.add(critical_node)

    return S
