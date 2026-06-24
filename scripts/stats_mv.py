import pandas as pd

INPUT = "resultados_wv_raw.csv"
OUTPUT = "resultados_wv_stats.csv"

df = pd.read_csv(INPUT)

# Converte colunas
df["Tempo"] = pd.to_numeric(df["Tempo"], errors="coerce")
df["Lucro"] = pd.to_numeric(df["Lucro"], errors="coerce")

# Agrupamento
stats = (
    df.groupby(["N", "W", "V", "Metodo"])
    .agg(
        Tempo_Medio=("Tempo", "mean"),
        Tempo_Std=("Tempo", "std"),
        Lucro_Medio=("Lucro", "mean"),
        Timeout_Perc=("Timeout", "mean")
    )
    .reset_index()
)

# Ajustes finais
stats["Tempo_Medio"] = stats["Tempo_Medio"].round(5)
stats["Tempo_Std"] = stats["Tempo_Std"].round(5)
stats["Lucro_Medio"] = stats["Lucro_Medio"].round(5)
stats["Timeout_Perc"] = (stats["Timeout_Perc"] * 100).round(2)

stats.to_csv(OUTPUT, index=False)

print("✅ Estatísticas geradas em", OUTPUT)
