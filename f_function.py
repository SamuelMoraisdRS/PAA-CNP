"""
Implementacao da funcao objetivo "f" para o Problema dos Nos Criticos (CNP).

f(G \\ S) = somatorio de C(|Ci|, 2), sendo Ci os componentes conexos do grafo G apos remocao dos vertices de S.
O somatorio retorna, portanto o numero de pares conectados de G \\ S.
"""

from __future__ import annotations

from collections import deque

from graph import Graph


"""
Implementacao de C(n, 2). Retorna o numero de pares conectados em um componente com n vertices.
Usada para retornar o valor efetivo da funcao objetivo "f"
"""


def pairs(size: int) -> int:

    return size * (size - 1) // 2


"""
Funcao objetivo 'f', que deve ser minimizada pela abordagem gulosa. Retorna o numero de pares conectados em G mediante a exclusao do conjunto S de vertices.

Performa uma BFS tomando cada vertice V de G \\ S que ainda nao foi visitado como raiz, para encontrar os componentes conexos (vertices alcancaveis a partir de V).
Com o numero de vertices nos componentes usamos a funcao @pairs para calcular o numero de pares conexos neles
"""


def f_function(graph: Graph, S: set[int]) -> int:
    """Computes f(G \\ S) from scratch with a BFS per component, O(n+m)."""
    n = graph.num_vertices()

    # Marca os vertices excluidos como visitados para nao fazer sua BFS
    visited = [False] * n
    for v in S:
        visited[v] = True

    total = 0

    for source in range(n):
        # desconsiderando vertices de S
        if visited[source]:
            continue

        visited[source] = True
        # Pilha da BFS
        queue = deque([source])
        size = 0
        # loop da BFS
        while queue:
            u = queue.popleft()
            size += 1
            for w in graph.adj_list[u]:
                if not visited[w]:
                    visited[w] = True
                    queue.append(w)

        # Adiciona o numero de pares ao total global de G \\ S
        total += pairs(size)

    return total
