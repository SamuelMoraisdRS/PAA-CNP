"""
Algoritmo 'greedy2'  de Addis et al. com a otimizacao de
Ventresca e Aleman (2015).

Para evitar calcular f para cada vertice candidato, é feita uma DFS para
computar f(G \\ (S U {v})) para todos os vertices v de uma só vez. Cada iteração
terá custo O(|V|+|E|), com as k iterações, temos a complexidade O(k*(|V|+|E|))
"""

from __future__ import annotations

from graph import Graph

from f_function import pairs

import math


"""Implementação do evaluate_all baseado no pseudocódigo apresentado por Ventresca e Aleman (2015)"""


def evaluate_all(graph: Graph, removed: set[int]) -> list[int | None]:
    n = graph.num_vertices()
    adj = graph.adj_list

    is_removed = [False] * n
    for v in removed:
        is_removed[v] = True

    # vetor de |V| posições para armazenar a ordem na qual o vertice v foi visitado.
    # Inicializa com -1 para indicar nenhuma visita.
    dfn = [-1] * n

    # Vetor de |V| posições para armazenar o menor valor do vetor dfn que pode ser alcançado a partir da subárvore com raíz v usando uma aresta de retorno.
    low = [0] * n

    # Vetor de |V| posições com os os tamanhos das subarvores com raiz v
    subtree_size = [1] * n

    # Vetor de |V| posições com o identificador do pai do vertice v
    parent = [-1] * n

    # vetor da DFS iterativa. next_neigh[v] mantem a posicao do ultimo vizinho explorado para o vertice v.
    next_neigh = [0] * n

    # Vetor que agrega o tamanho da subárvore removida ao retirar o vértice v
    cut_mass = [0] * n

    # relacionado como vetor cut_mass, guarda o número de pares conexos na subárvore de raiz v
    split_value = [0] * n

    # Conectividade par a par do grafo residual se o vertice v é removido.
    # NOTE : Inicializamos cada posicao com None ao invés de 0, pois pode ser que
    # a remocao do vertice resulte no valor de f como 0. O None diferencia que o vértice não foi analisado
    result = [None] * n

    # Valor total de f
    total_f = 0

    # Contador de passos da DFS, para preencher o vetor dfn
    counter = 0

    for root in range(n):
        if is_removed[root] or dfn[root] != -1:
            continue

        # dfs iterativa
        dfn[root] = low[root] = counter
        counter += 1
        component = [root]
        stack = [root]
        while stack:
            v = stack[-1]
            # Se existe vizinho de v não explorado, seguimos com a dfs
            if next_neigh[v] < len(adj[v]):
                w = adj[v][next_neigh[v]]
                next_neigh[v] += 1
                if is_removed[w] or w == parent[v]:
                    continue
                # se não foi visitado, segue a dfs
                if dfn[w] == -1:
                    parent[w] = v
                    dfn[w] = low[w] = counter
                    counter += 1
                    component.append(w)
                    stack.append(w)
                else:
                    # Se já foi visitado, temos uma aresta de retorno
                    #
                    low[v] = min(low[v], dfn[w])
            else:
                # Se não existe vizinho não explorado de v, então a subarvore de v
                # esta completa e podemos passar os valores para o pai
                stack.pop()
                p = parent[v]
                if p != -1:
                    low[p] = min(low[p], low[v])
                    subtree_size[p] += subtree_size[v]
                    # Com a subarvore explorado, checa se nao existe aresta de retorno na subarvore para algum antecedente de v.
                    # Se não existir, entao o vertice v é ponto de corte que isola a subarvore e gera um componente.
                    if low[v] >= dfn[p]:
                        cut_mass[p] += subtree_size[v]
                        split_value[p] += pairs(subtree_size[v])

        comp_size = len(component)
        comp_pairs = pairs(comp_size)
        total_f += comp_pairs
        for v in component:
            # Calculo do restante do grafo residual descontando o componente atual.
            # o cálculo é melhor explicado no trabalho de Ventresca
            remainder = comp_size - 1 - cut_mass[v]

            # Preenchendo o valor de f para a remocao de v contando apenas o PRÓPRIO COMPONENTE GERADO POR V.
            # O valor final depende do f total
            result[v] = split_value[v] + pairs(remainder) - comp_pairs

    # NOTE : Soma os valores de f por componente com o f total. O f total só é obtido depois de processar todos os componentes individualmente, então precisa ser feito depois do loop principal. adiciona custo |V|.
    for v in range(n):
        if result[v] is not None:
            result[v] += total_f

    return result


"""Implementação adaptada do greedy2 utilizando a otimização. A estrutura permanece a mesma, trocando apenas a lógica de seleção"""


def greedy2_dfs(graph: Graph, k: int) -> tuple[list[int], list[int]]:
    S = set()
    order = []
    history = []
    k = min(k, graph.num_vertices())
    while len(S) < k:
        values = evaluate_all(graph, S)
        critical_node = None
        lowest_f_value = math.inf
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
