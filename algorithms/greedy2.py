"""
'greedy2' algorithm implementation, as presented by Addis et al.

"""

from graph import Graph

from f_function import f_function

import math


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
