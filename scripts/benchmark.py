#!/usr/bin/env python3
import subprocess
import time
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEN = os.path.join(ROOT, "input_files", "generator")
EXEC = os.path.join(ROOT, "app", "exe")
INPUT_DIR = os.path.join(ROOT, "input_files")

NS = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
W_VALUES = [100]
V_VALUES = [100]
INSTANCES_PER_COMBINATION = 10
METHODS = ["dynamic", "backtracking", "bnb"]
TIMEOUT = 7200
CSV_RAW = os.path.join(ROOT, "resultados_raw.csv")

def gerar_instancias(n, w, v):
    subprocess.run(
        [GEN, str(n), str(w), str(v)],
        cwd=INPUT_DIR,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

def caminho_instancia(n, w, v, instance_id):
    name = f"instancia_n{n}_W{w}_V{v}_i{instance_id}.txt"
    return os.path.join(INPUT_DIR, name)

def rodar(metodo, instancia):
    start = time.time()
    try:
        result = subprocess.run(
            [EXEC, instancia, metodo],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=TIMEOUT
        )
        elapsed = time.time() - start

        lucro = None
        for line in result.stdout.splitlines():
            if "Lucro máximo" in line:
                lucro = float(line.split("R$")[1].strip())
                break

        return lucro, elapsed, False

    except subprocess.TimeoutExpired:
        return None, TIMEOUT, True

total_tests = (
    len(NS) * len(W_VALUES) * len(V_VALUES) *
    INSTANCES_PER_COMBINATION * len(METHODS)
)
current_test = 0

with open(CSV_RAW, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "N", "W", "V", "Instancia", "Metodo",
        "Lucro", "Tempo", "Timeout"
    ])

    for n in NS:
        for w in W_VALUES:
            for v in V_VALUES:
                gerar_instancias(n, w, v)

                for instance_id in range(1, INSTANCES_PER_COMBINATION + 1):
                    instancia = caminho_instancia(n, w, v, instance_id)

                    for metodo in METHODS:
                        current_test += 1
                        print(
                            f"[{current_test}/{total_tests}] "
                            f"N={n} W={w} V={v} Instancia={instance_id}/10 Metodo={metodo}",
                            flush=True
                        )

                        lucro, tempo, timeout = rodar(metodo, instancia)

                        writer.writerow([
                            n, w, v, instance_id, metodo,
                            f"{lucro:.5f}" if lucro is not None else "",
                            f"{tempo:.5f}",
                            timeout
                        ])
                        f.flush()

print(f"\nBenchmark finalizado. Dados salvos em {CSV_RAW}")
