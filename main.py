"""
Command line interface for the Critical Node Problem (CNP) solved with the
'greedy2' constructive heuristic (Addis et al.).

Usage (from any folder): python3 main.py

The user picks an instance, K and the algorithm version; the experiment
report and the best solution found are shown on screen and saved in
'resultados/'. Only the Python standard library is used.
"""

# Allows annotations like list[int] on Python < 3.9
from __future__ import annotations

import csv
import os
import re
import textwrap
import time

from graph import Graph
from f_function import f_function
from algorithms.greedy2 import greedy2
from algorithms.greedy2_dfs import greedy2_dfs

# Paths are relative to this file, so the program works from any folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INSTANCE_DIRS = ["Ventresca", "testes"]
RESULTS_DIR = os.path.join(BASE_DIR, "resultados")

# (K, best known objective value) of each instance.
# Synthetic benchmark of Ventresca (2012). K and best known values from
# Zhou, Hao & Glover (2019), "Memetic search for identifying critical nodes
# in sparse graphs", IEEE Transactions on Cybernetics, Table IV.
INSTANCES = {
    "BarabasiAlbert_n500m1": (50, 195),
    "BarabasiAlbert_n1000m1": (75, 558),
    "BarabasiAlbert_n2500m1": (100, 3704),
    "BarabasiAlbert_n5000m1": (150, 10196),
    "ErdosRenyi_n250": (50, 295),
    "ErdosRenyi_n500": (80, 1524),
    "ErdosRenyi_n1000": (140, 5012),
    "ErdosRenyi_n2500": (200, 902498),
    "ForestFire_n250": (50, 194),
    "ForestFire_n500": (110, 257),
    "ForestFire_n1000": (150, 1260),
    "ForestFire_n2000": (200, 4545),
    "WattsStrogatz_n250": (70, 3083),
    "WattsStrogatz_n500": (125, 2072),
    "WattsStrogatz_n1000": (200, 109807),
    "WattsStrogatz_n1500": (265, 13098),
    # Example from the study notes; 2 is the optimum for K=2, found by
    # exhaustive search in validar.py (greedy2 finds 3)
    "exemplo7": (2, 2),
}

ALGORITHMS = {
    "dfs": ("greedy2 rápido (DFS + pontos de articulação), O(k(n+m))", greedy2_dfs),
    "ingenuo": ("greedy2 ingênuo (recalcula f do zero), O(k·n·(n+m))", greedy2),
}

LINE = "=" * 70
# Backslashes are not allowed inside f-string braces before Python 3.12
F_LABEL = "f(G\\R)"


def natural_key(name: str) -> list:
    """Sorts 'n500' before 'n1000' (plain string sorting would not)."""
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]


def list_instances() -> list[tuple[str, str]]:
    """(name, path) of every instance file, benchmark first."""
    instances = []
    for folder in INSTANCE_DIRS:
        folder_path = os.path.join(BASE_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        names = [f[:-4] for f in os.listdir(folder_path) if f.endswith(".txt")]
        for name in sorted(names, key=natural_key):
            instances.append((name, os.path.join(folder_path, name + ".txt")))
    return instances


def run_experiment(name: str, path: str, k: int, alg_key: str) -> dict:
    graph = Graph(path)
    description, algorithm = ALGORITHMS[alg_key]

    start = time.perf_counter()
    order, history = algorithm(graph, k)
    elapsed = time.perf_counter() - start

    # Independent check: recompute the final value from scratch
    final_f = f_function(graph, set(order))
    if history and history[-1] != final_f:
        raise RuntimeError(
            f"Inconsistência: o algoritmo informou f={history[-1]}, "
            f"mas f_function calculou {final_f}"
        )

    return {
        "name": name,
        "path": path,
        "n": graph.num_vertices(),
        "m": graph.num_edges(),
        "k": k,
        "alg_key": alg_key,
        "description": description,
        "time": elapsed,
        "initial_f": f_function(graph, set()),
        "final_f": final_f,
        "best_known": INSTANCES.get(name, (None, None))[1],
        "order": order,
        "history": history,
    }


def gap_text(value: int, best_known) -> str:
    if best_known is None:
        return "—"
    if best_known == 0:
        return "0.00%" if value == 0 else "—"
    return f"{100 * (value - best_known) / best_known:+.2f}%"


def field(label: str, value) -> str:
    return f"{label} ".ljust(26, ".") + f" {value}"


def wrap_list(values: list[int]) -> str:
    if not values:
        return "  (vazio)"
    return textwrap.fill(
        " ".join(str(v) for v in values),
        width=70, initial_indent="  ", subsequent_indent="  ",
    )


def format_report(r: dict) -> str:
    best = r["best_known"] if r["best_known"] is not None else "—"
    lines = [
        LINE,
        "RELATÓRIO DO EXPERIMENTO — Problema dos Nós Críticos (CNP)",
        LINE,
        field("Instância", r["name"]),
        field("Arquivo", os.path.relpath(r["path"], BASE_DIR)),
        field("Vértices (n)", r["n"]),
        field("Arestas (m)", r["m"]),
        field("K (máx. de remoções)", r["k"]),
        field("Algoritmo", r["description"]),
        field("Tempo de execução", f"{r['time']:.3f} s"),
        field("f(G) sem remoções", r["initial_f"]),
        field("f(G\\R) obtido", r["final_f"]),
        field("Melhor valor conhecido", best),
        field("Gap para o melhor", gap_text(r["final_f"], r["best_known"])),
        "",
        "MELHOR SOLUÇÃO ENCONTRADA",
        field("|R|", len(r["order"])),
        field("f(G\\R)", r["final_f"]),
        "R (na ordem de escolha):",
        wrap_list(r["order"]),
        "R (ordenado):",
        wrap_list(sorted(r["order"])),
        LINE,
    ]
    return "\n".join(lines)


def format_history(r: dict) -> str:
    lines = [
        "EVOLUÇÃO DE f(G\\R) A CADA ITERAÇÃO",
        f"{'iteração':>10} {'vértice removido':>18} {F_LABEL:>12}",
    ]
    for i, (v, value) in enumerate(zip(r["order"], r["history"]), start=1):
        lines.append(f"{i:>10} {v:>18} {value:>12}")
    return "\n".join(lines)


def save_report(r: dict) -> str:
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_path = os.path.join(RESULTS_DIR, f"{r['name']}_{r['alg_key']}.txt")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(format_report(r) + "\n\n" + format_history(r) + "\n")
    return out_path


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        # Input closed (e.g. Ctrl+D): leave quietly
        print()
        raise SystemExit(0)


def choose_k(name: str) -> int:
    default = INSTANCES.get(name, (None, None))[0]
    hint = f" [Enter = {default}]" if default is not None else ""
    while True:
        answer = ask(f"Valor de K{hint}: ")
        if not answer and default is not None:
            return default
        if answer.isdigit():
            return int(answer)
        print("  K deve ser um número inteiro >= 0.")


def choose_algorithm() -> str:
    print("Algoritmo:")
    print("  1) greedy2 rápido (DFS + pontos de articulação)")
    print("  2) greedy2 ingênuo (recalcula f do zero; lento nas instâncias grandes)")
    while True:
        answer = ask("Escolha [Enter = 1]: ")
        if answer in ("", "1"):
            return "dfs"
        if answer == "2":
            print("  Aviso: nas instâncias com milhares de vértices a versão "
                  "ingênua pode levar vários minutos.")
            return "ingenuo"
        print("  Opção inválida.")


def run_one(name: str, path: str) -> None:
    k = choose_k(name)
    alg_key = choose_algorithm()
    print("\nExecutando...\n")
    r = run_experiment(name, path, k, alg_key)
    print(format_report(r))
    out_path = save_report(r)
    print(f"Relatório completo (com a evolução de f) salvo em: "
          f"{os.path.relpath(out_path, BASE_DIR)}")


def run_all(instances: list[tuple[str, str]]) -> None:
    benchmark = [(name, path) for name, path in instances
                 if os.path.basename(os.path.dirname(path)) == "Ventresca"
                 and name in INSTANCES]
    alg_key = choose_algorithm()
    print()

    results = []
    for i, (name, path) in enumerate(benchmark, start=1):
        k = INSTANCES[name][0]
        print(f"[{i:>2}/{len(benchmark)}] {name:<24} K={k:<4}", end=" ", flush=True)
        r = run_experiment(name, path, k, alg_key)
        save_report(r)
        results.append(r)
        print(f"f(G\\R)={r['final_f']:<8} ({r['time']:.2f} s)")

    header = (f"{'Instância':<24} {'n':>5} {'m':>6} {'K':>4} {F_LABEL:>9} "
              f"{'melhor':>9} {'gap':>9} {'tempo(s)':>9}")
    print("\n" + LINE)
    print(f"RESUMO — {ALGORITHMS[alg_key][0]}")
    print(LINE)
    print(header)
    for r in results:
        print(f"{r['name']:<24} {r['n']:>5} {r['m']:>6} {r['k']:>4} "
              f"{r['final_f']:>9} {r['best_known']:>9} "
              f"{gap_text(r['final_f'], r['best_known']):>9} {r['time']:>9.3f}")

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, f"tabela_{alg_key}.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["instancia", "n", "m", "K", "algoritmo", "f_obtido",
                         "melhor_conhecido", "gap_percent", "tempo_s"])
        for r in results:
            gap = 100 * (r["final_f"] - r["best_known"]) / r["best_known"]
            writer.writerow([r["name"], r["n"], r["m"], r["k"], alg_key,
                             r["final_f"], r["best_known"], f"{gap:.2f}",
                             f"{r['time']:.3f}"])
    print(f"\nTabela salva em: {os.path.relpath(csv_path, BASE_DIR)}")
    print("Relatórios individuais salvos em: resultados/<instancia>_"
          f"{alg_key}.txt")


def print_menu(instances: list[tuple[str, str]]) -> None:
    print("\n" + LINE)
    print("PROBLEMA DOS NÓS CRÍTICOS (CNP) — guloso greedy2")
    print(LINE)
    print("Instâncias disponíveis:")
    for i, (name, path) in enumerate(instances, start=1):
        folder = os.path.basename(os.path.dirname(path))
        k = INSTANCES.get(name, (None, None))[0]
        k_text = f"K={k}" if k is not None else "K=?"
        print(f"  {i:>2}) {name:<26} {k_text:<7} ({folder})")
    print("   T) Rodar todas as instâncias do benchmark (gera a tabela)")
    print("   S) Sair")


def main() -> None:
    instances = list_instances()
    while True:
        print_menu(instances)
        choice = ask("Escolha uma opção: ").upper()
        if choice == "S":
            break
        if choice == "T":
            run_all(instances)
        elif choice.isdigit() and 1 <= int(choice) <= len(instances):
            name, path = instances[int(choice) - 1]
            run_one(name, path)
        else:
            print("Opção inválida.")


if __name__ == "__main__":
    main()
