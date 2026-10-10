"""
Validation of the implementation. Usage (from any folder): python3 validar.py

1. 7-vertex example from the study notes: values checked by hand.
2. Random small graphs: evaluate_all (fast, one DFS) must match f_function
   (computed from scratch) for every vertex and several removed sets.
3. Random small graphs: greedy2 (naive) and greedy2_dfs (fast) must choose
   exactly the same vertices.
4. Smallest benchmark instances: same comparison, with the real K.
5. Exhaustive search on the 7-vertex example: the greedy is never better
   than the optimum (and is not always optimal).
"""

# Allows annotations like list[int] on Python < 3.9
from __future__ import annotations

import itertools
import os
import random
import sys
import time

from graph import Graph
from f_function import f_function
from algorithms.greedy2 import greedy2
from algorithms.greedy2_dfs import evaluate_all, greedy2_dfs
from main import BASE_DIR, INSTANCES

SMALL_INSTANCES = [
    "ErdosRenyi_n250",
    "ForestFire_n250",
    "WattsStrogatz_n250",
    "BarabasiAlbert_n500m1",
]

failures = 0


def check(description: str, condition: bool) -> None:
    global failures
    if not condition:
        failures += 1
    print(f"  [{'OK' if condition else 'FALHOU'}] {description}")


def random_graph(rng: random.Random, n: int, p: float) -> Graph:
    adj = [[] for _ in range(n)]
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                adj[u].append(v)
                adj[v].append(u)
    # Some parallel edges, like the ones found in WattsStrogatz_n1000.txt
    for u in range(n):
        if adj[u] and rng.random() < 0.1:
            v = rng.choice(adj[u])
            adj[u].append(v)
            adj[v].append(u)
    # Random neighbour order, so the DFS explores edges in varied orders
    for neigh in adj:
        rng.shuffle(neigh)
    return Graph.from_adj_list(adj)


def test_example() -> None:
    print("1) Exemplo de 7 vértices (paa.md, seção 4)")
    g = Graph(os.path.join(BASE_DIR, "testes", "exemplo7.txt"))
    expected = [15, 15, 7, 6, 15, 10, 15]
    check("f(G) = 21", f_function(g, set()) == 21)
    check(f"f_function(G\\{{v}}) para v=0..6 = {expected}",
          [f_function(g, {v}) for v in range(7)] == expected)
    check("evaluate_all(G, {}) bate com a mesma tabela",
          evaluate_all(g, set()) == expected)
    for name, algorithm in (("greedy2", greedy2), ("greedy2_dfs", greedy2_dfs)):
        check(f"{name}, k=4: R=[3, 5, 0, 1] e f=[6, 3, 1, 0]",
              algorithm(g, 4) == ([3, 5, 0, 1], [6, 3, 1, 0]))
        check(f"{name}, k=99 (> n): termina e para quando f chega a 0",
              algorithm(g, 99) == ([3, 5, 0, 1], [6, 3, 1, 0]))


def test_random_evaluation(rng: random.Random, n_graphs: int = 300) -> None:
    print("2) evaluate_all × f_function em grafos aleatórios")
    comparisons = mismatches = 0
    for _ in range(n_graphs):
        n = rng.randint(1, 40)
        g = random_graph(rng, n, rng.uniform(0.02, 0.5))
        for _ in range(5):
            removed = set(rng.sample(range(n), rng.randint(0, n // 2)))
            fast = evaluate_all(g, removed)
            for v in range(n):
                if v in removed:
                    ok = fast[v] is None
                else:
                    ok = fast[v] == f_function(g, removed | {v})
                comparisons += 1
                mismatches += not ok
    check(f"{comparisons} comparações em {n_graphs} grafos, "
          f"{mismatches} divergências", mismatches == 0)


def test_random_greedy(rng: random.Random, n_graphs: int = 100) -> None:
    print("3) greedy2 × greedy2_dfs em grafos aleatórios")
    differences = 0
    for _ in range(n_graphs):
        n = rng.randint(1, 30)
        g = random_graph(rng, n, rng.uniform(0.02, 0.5))
        k = rng.randint(0, n)
        if greedy2(g, k) != greedy2_dfs(g, k):
            differences += 1
    check(f"{n_graphs} grafos, {differences} com escolhas diferentes",
          differences == 0)


def test_small_instances() -> None:
    print("4) greedy2 × greedy2_dfs nas menores instâncias do benchmark")
    for name in SMALL_INSTANCES:
        g = Graph(os.path.join(BASE_DIR, "Ventresca", name + ".txt"))
        k = INSTANCES[name][0]
        start = time.perf_counter()
        naive = greedy2(g, k)
        t_naive = time.perf_counter() - start
        start = time.perf_counter()
        fast = greedy2_dfs(g, k)
        t_fast = time.perf_counter() - start
        check(f"{name} (K={k}): f={fast[1][-1]}, mesmas escolhas; "
              f"ingênuo {t_naive:.2f} s × rápido {t_fast:.2f} s",
              naive == fast)


def test_exhaustive() -> None:
    print("5) Força bruta exaustiva no exemplo de 7 vértices")
    g = Graph(os.path.join(BASE_DIR, "testes", "exemplo7.txt"))
    for k in (1, 2, 3):
        optimum = min(f_function(g, set(c))
                      for c in itertools.combinations(range(7), k))
        greedy_value = greedy2_dfs(g, k)[1][-1]
        check(f"k={k}: ótimo={optimum}, greedy2={greedy_value} "
              f"(o guloso nunca é melhor que o ótimo)", greedy_value >= optimum)
        if k == INSTANCES["exemplo7"][0]:
            check(f"k={k}: ótimo bate com o valor de referência em main.py "
                  f"({INSTANCES['exemplo7'][1]})",
                  optimum == INSTANCES["exemplo7"][1])


def main() -> None:
    rng = random.Random(2026)  # fixed seed: the same graphs on every run
    test_example()
    test_random_evaluation(rng)
    test_random_greedy(rng)
    test_small_instances()
    test_exhaustive()
    print()
    if failures:
        print(f"{failures} verificação(ões) falharam.")
        sys.exit(1)
    print("Todas as verificações passaram.")


if __name__ == "__main__":
    main()
