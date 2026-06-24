import pandas as pd
import numpy as np
from scipy.stats import t

INPUT = "../resultados_raw.csv"
OUTPUT = "../resultados_stats.csv"

df = pd.read_csv(INPUT)

# remove execuções com timeout
df = df[df["Timeout"] == False]

grouped = df.groupby(["N", "W", "V", "Metodo"])

rows = []

for (n, w, v, metodo), g in grouped:
    tempos = g["Tempo"].astype(float)
    lucros = g["Lucro"].astype(float)

    mean_t = tempos.mean()
    std_t = tempos.std(ddof=1)
    ci = t.ppf(0.975, len(tempos)-1) * std_t / np.sqrt(len(tempos))

    rows.append([
        n, w, v, metodo,
        f"{lucros.mean():.5f}",
        f"{mean_t:.5f}",
        f"{std_t:.5f}",
        f"{ci:.5f}"
    ])

out = pd.DataFrame(rows, columns=[
    "N", "W", "V", "Metodo",
    "Lucro_Medio",
    "Tempo_Medio",
    "Desvio_Padrao",
    "IC_95"
])

out.to_csv(OUTPUT, index=False)
print("✅ Estatísticas salvas em resultados_stats.csv")
