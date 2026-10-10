"""
'greedy2' algorithm implementation, as presented by Addis et al.

Naive version: every candidate vertex is evaluated by recomputing the
objective function from scratch, so each iteration costs O(n(n+m)) and the
whole algorithm O(k n (n+m)).
"""

# Allows annotations like set[int] on Python < 3.9
from __future__ import annotations

from graph import Graph

from f_function import f_function

import math


def greedy2(graph: Graph, k: int) -> tuple[list[int], list[int]]:
    """
    Returns the removed vertices in the order they were chosen and the value
    of f(G \\ S) after each iteration.
    """
    S = set()
    order = []
    history = []
    # With k > n the loop would never finish (no candidate left to add)
    k = min(k, graph.num_vertices())
    while len(S) < k:
        critical_node = None
        lowest_f_value = math.inf
        # i = argmax (f(S) - f(S U {i})) = argmin f(S U {i})
        # Ties are broken by the lowest index (strict '<')
        for i in range(graph.num_vertices()):
            if i in S:
                continue
            curr_f_value = f_function(graph, S | {i})
            if curr_f_value < lowest_f_value:
                lowest_f_value = curr_f_value
                critical_node = i

        S.add(critical_node)
        order.append(critical_node)
        history.append(lowest_f_value)
        # No edge left: removing more vertices cannot improve f
        if lowest_f_value == 0:
            break

    return order, history
