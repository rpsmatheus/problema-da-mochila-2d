#!/usr/bin/env python3
import subprocess
import csv
import time
import os

N_VALUES = [50]
W_VALUES = [50, 100, 150, 200, 300]
V_VALUES = [50, 100, 150, 200, 300]
METHODS = ["dynamic", "bnb", "backtracking"]
INSTANCES_PER_COMBINATION = 10
TIMEOUT = 3600

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEC = os.path.join(ROOT, "app", "exe")
GEN = os.path.join(ROOT, "input_files", "generator")
INPUT_DIR = os.path.join(ROOT, "input_files")
OUT_CSV = os.path.join(ROOT, "scripts", "resultados_wv_raw.csv")

def gerar_instancias(n, w, v):
    subprocess.run(
        [GEN, str(n), str(w), str(v)],
        cwd=INPUT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

def caminho_instancia(n, w, v, instance_id):
    name = f"instancia_n{n}_W{w}_V{v}_i{instance_id}.txt"
    return os.path.join(INPUT_DIR, name)

def rodar_algoritmo(instancia, metodo):
    start = time.time()
    try:
        result = subprocess.run(
            [EXEC, instancia, metodo],
            cwd=ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT,
            text=True
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

total = (
    len(N_VALUES) * len(W_VALUES) * len(V_VALUES) *
    INSTANCES_PER_COMBINATION * len(METHODS)
)
progress = 0

with open(OUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "N", "W", "V", "Instancia", "Metodo",
        "Lucro", "Tempo", "Timeout"
    ])

    for n in N_VALUES:
        for w in W_VALUES:
            for v in V_VALUES:
                print(f"\n=== N={n} | W={w} | V={v} ===")
                gerar_instancias(n, w, v)

                for instance_id in range(1, INSTANCES_PER_COMBINATION + 1):
                    instancia = caminho_instancia(n, w, v, instance_id)

                    for metodo in METHODS:
                        progress += 1
                        print(
                            f"[{progress}/{total}] "
                            f"Instancia={instance_id}/10 Metodo={metodo}",
                            flush=True
                        )

                        lucro, tempo, timeout = rodar_algoritmo(instancia, metodo)

                        writer.writerow([
                            n, w, v, instance_id, metodo,
                            f"{lucro:.5f}" if lucro is not None else "",
                            f"{tempo:.5f}",
                            int(timeout)
                        ])
                        f.flush()

print(f"\nBenchmark W/V finalizado. Dados salvos em {OUT_CSV}")
