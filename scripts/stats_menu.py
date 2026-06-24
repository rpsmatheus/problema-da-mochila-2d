#!/usr/bin/env python3
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_SITE_PACKAGES = ROOT / "scripts" / "venv" / "lib" / "python3.12" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

import pandas as pd

try:
    from scipy.stats import t
except ImportError:
    t = None

INPUT = ROOT / "resultados_experimentos.csv"
OUTPUT = ROOT / "resultados_experimentos_stats.csv"


def intervalo_confianca_95(serie):
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    n = len(valores)
    if n <= 1:
        return 0.0

    std = valores.std(ddof=1)
    if pd.isna(std):
        return 0.0

    fator = t.ppf(0.975, n - 1) if t is not None else 1.96
    return fator * std / math.sqrt(n)


def main():
    if not INPUT.exists():
        raise SystemExit(f"Arquivo nao encontrado: {INPUT}")

    df = pd.read_csv(INPUT)
    df["Tempo"] = pd.to_numeric(df["Tempo"], errors="coerce")
    df["Lucro"] = pd.to_numeric(df["Lucro"], errors="coerce")
    df["Timeout"] = pd.to_numeric(df["Timeout"], errors="coerce").fillna(0).astype(int)

    rows = []
    grouped = df.groupby(["N", "W", "V", "Metodo"], sort=True)

    for (n, w, v, metodo), grupo in grouped:
        total_execucoes = len(grupo)
        timeouts = int(grupo["Timeout"].sum())
        timeout_perc = (timeouts / total_execucoes) * 100 if total_execucoes else 0.0

        sem_timeout = grupo[grupo["Timeout"] == 0]
        tempos = sem_timeout["Tempo"]
        lucros = sem_timeout["Lucro"]

        rows.append({
            "N": n,
            "W": w,
            "V": v,
            "Metodo": metodo,
            "Execucoes": total_execucoes,
            "Execucoes_Validas": len(sem_timeout),
            "Timeouts": timeouts,
            "Timeout_%": round(timeout_perc, 2),
            "Lucro_Medio": round(lucros.mean(), 5) if lucros.notna().any() else "",
            "Tempo_Medio": round(tempos.mean(), 5) if tempos.notna().any() else "",
            "Tempo_Desvio_Padrao": round(tempos.std(ddof=1), 5) if tempos.notna().sum() > 1 else 0.0,
            "Tempo_IC_95": round(intervalo_confianca_95(tempos), 5) if tempos.notna().any() else "",
        })

    stats = pd.DataFrame(rows, columns=[
        "N", "W", "V", "Metodo", "Execucoes", "Execucoes_Validas",
        "Timeouts", "Timeout_%", "Lucro_Medio", "Tempo_Medio",
        "Tempo_Desvio_Padrao", "Tempo_IC_95",
    ])
    stats.to_csv(OUTPUT, index=False)
    print(f"Tabela estatistica gerada em: {OUTPUT}")


if __name__ == "__main__":
    main()
