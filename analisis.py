import argparse
import csv
import os
import time
import statistics
from dataclasses import dataclass
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
from Turing import TuringMachine


@dataclass
class ExperimentRow:
    m: int
    k: int
    time_sec_median: float
    time_sec_mean: float
    time_sec_std: float
    runs: int


def run_until_halt(tm: TuringMachine, max_steps: int = 300000) -> int:
    """
    Ejecuta la MT hasta aceptar o quedarse sin transición.
    Devuelve pasos ejecutados (solo por si querés loguearlo).
    """
    steps = 0
    while tm.state not in tm.accepting and steps < max_steps:
        progressed = tm.step()
        if not progressed:
            break
        steps += 1
    return steps


def build_input_for_suma(m: int, k: int) -> Tuple[List[str], List[int] | None]:
    """
    Para Suma.json:
      - Cinta 0: dummy
      - Cinta 1: m unos (entrada)
      - Cinta 2: k unos (acumulador inicial)
    """
    tape0 = "_"
    tape1 = "1" * m
    tape2 = "1" * k
    return [tape0, tape1, tape2], None


def measure_time_one_run(json_path: str, m: int, k: int, max_steps: int) -> float:
    """
    Una medición de tiempo (segundos) para un (m,k).
    IMPORTANTÍSIMO: Creamos una instancia nueva por run para evitar “estado residual”.
    """
    tm = TuringMachine(config_file=json_path, num_tapes=3)

    # Optimización para que el tiempo refleje más “cómputo” y menos logging:
    # tu step() guarda history en log_step(). Eso mete overhead grande.
    # Para medir ejecución pura, desactivamos el log_step.
    tm.log_step = lambda: None
    tm.history = []

    tapes_content, head_positions = build_input_for_suma(m, k)
    tm.load_input(tapes_content=tapes_content, head_positions=head_positions)

    t0 = time.perf_counter()
    run_until_halt(tm, max_steps=max_steps)
    t1 = time.perf_counter()
    return t1 - t0


def run_experiments(json_path: str, m_max: int, k_values: List[int], runs: int, warmup: int, max_steps: int) -> List[ExperimentRow]:
    rows: List[ExperimentRow] = []

    for k in k_values:
        for m in range(1, m_max + 1):
            # Warmup: estabiliza caches/JIT internos del sistema (Python no JIT, pero igual ayuda por CPU cache)
            for _ in range(warmup):
                _ = measure_time_one_run(json_path, m, k, max_steps)

            times = [measure_time_one_run(json_path, m, k, max_steps) for _ in range(runs)]

            median_t = statistics.median(times)
            mean_t = statistics.mean(times)
            std_t = statistics.pstdev(times) if len(times) > 1 else 0.0

            rows.append(ExperimentRow(
                m=m,
                k=k,
                time_sec_median=median_t,
                time_sec_mean=mean_t,
                time_sec_std=std_t,
                runs=runs
            ))

    return rows


def save_csv(rows: List[ExperimentRow], out_csv: str) -> None:
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["m", "k", "time_sec_median", "time_sec_mean", "time_sec_std", "runs"])
        for r in rows:
            w.writerow([r.m, r.k, r.time_sec_median, r.time_sec_mean, r.time_sec_std, r.runs])


def plot_scatter(rows: List[ExperimentRow], out_png: str) -> None:
    by_k: Dict[int, List[ExperimentRow]] = {}
    for r in rows:
        by_k.setdefault(r.k, []).append(r)

    plt.figure(figsize=(10, 6))
    for k, items in sorted(by_k.items()):
        xs = [it.m for it in items]
        ys = [it.time_sec_median * 1000.0 for it in items]  # ms
        plt.scatter(xs, ys, label=f"k={k}")

    plt.title("Dispersión: Tiempo de ejecución vs tamaño de entrada")
    plt.xlabel("m = cantidad de '1' en la entrada")
    plt.ylabel("Tiempo de ejecución en milisegundos")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Análisis (tiempos) con diagrama de dispersión para MT")
    parser.add_argument("--json", required=True, help="Ruta del archivo JSON (ej: Suma.json)")
    parser.add_argument("--m_max", type=int, default=40, help="Máximo m. Default=40")
    parser.add_argument("--k", type=int, nargs="+", default=[0, 5, 10], help="Lista de k (acumulador). Default: 0 5 10")
    parser.add_argument("--runs", type=int, default=15, help="Repeticiones por punto. Default=15")
    parser.add_argument("--warmup", type=int, default=3, help="Warmup por punto. Default=3")
    parser.add_argument("--max_steps", type=int, default=400000, help="Límite de pasos por ejecución. Default=400000")
    parser.add_argument("--out_csv", default="results_time.csv", help="Salida CSV. Default=results_time.csv")
    parser.add_argument("--out_png", default="scatter_time.png", help="Salida PNG. Default=scatter_time.png")
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"Error: No existe el archivo JSON: {args.json}")
        return

    rows = run_experiments(
        json_path=args.json,
        m_max=args.m_max,
        k_values=args.k,
        runs=args.runs,
        warmup=args.warmup,
        max_steps=args.max_steps
    )

    save_csv(rows, args.out_csv)
    plot_scatter(rows, args.out_png)

    print(f"- CSV: {args.out_csv}")
    print(f"- PNG: {args.out_png}")


if __name__ == "__main__":
    main()