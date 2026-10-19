"""
Implementacao do 'greedy2', como proposto por Addis et al.

"""

from __future__ import annotations

from graph import Graph
from f_function import f_function


import math


def greedy2(graph: Graph, k: int) -> tuple[list[int], list[int]]:
    S = set()
    order = []
    history = []
    # guarda para o caso k > |V|
    k = min(k, graph.num_vertices())
    while len(S) < k:
        critical_node = None
        # menor valor encontrado para a funcao objetivo
        lowest_f_value = math.inf
        # i = argmax (f(S) - f(S U {i})) = argmin f(S U {i})
        for i in range(graph.num_vertices()):
            if i in S:
                continue
            # valor de f(S U {i})
            curr_f_value = f_function(graph, S | {i})
            if curr_f_value < lowest_f_value:
                lowest_f_value = curr_f_value
                critical_node = i

        S.add(critical_node)
        order.append(critical_node)
        history.append(lowest_f_value)
        # f = 0: nao sobrou nenhuma aresta, remover mais vertices nao diminui f
        if lowest_f_value == 0:
            break

    return order, history
