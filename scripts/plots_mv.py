import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

CSV = "resultados_wv_stats.csv"

df = pd.read_csv(CSV)

# ===============================
# 1. Tempo x W (V fixo)
# ===============================
V_FIXO = 100
subset = df[df["V"] == V_FIXO]

plt.figure(figsize=(8, 5))
sns.lineplot(
    data=subset,
    x="W",
    y="Tempo_Medio",
    hue="Metodo",
    marker="o"
)
plt.title(f"Tempo Médio x Peso da Mochila (V={V_FIXO})")
plt.xlabel("Capacidade de Peso (W)")
plt.ylabel("Tempo Médio (s)")
plt.grid(True)
plt.tight_layout()
plt.savefig("tempo_vs_W.png")
plt.close()

# ===============================
# 2. Tempo x V (W fixo)
# ===============================
W_FIXO = 100
subset = df[df["W"] == W_FIXO]

plt.figure(figsize=(8, 5))
sns.lineplot(
    data=subset,
    x="V",
    y="Tempo_Medio",
    hue="Metodo",
    marker="o"
)
plt.title(f"Tempo Médio x Volume da Mochila (W={W_FIXO})")
plt.xlabel("Capacidade de Volume (V)")
plt.ylabel("Tempo Médio (s)")
plt.grid(True)
plt.tight_layout()
plt.savefig("tempo_vs_V.png")
plt.close()

# ===============================
# 3. Heatmap (DP)
# ===============================
dp = df[df["Metodo"] == "dynamic"]

pivot = dp.pivot(index="W", columns="V", values="Tempo_Medio")

plt.figure(figsize=(7, 6))
sns.heatmap(
    pivot,
    annot=True,
    fmt=".4f",
    cmap="viridis"
)
plt.title("Heatmap - Tempo Médio (Programação Dinâmica)")
plt.xlabel("Volume (V)")
plt.ylabel("Peso (W)")
plt.tight_layout()
plt.savefig("heatmap_dp.png")
plt.close()

print("📊 Gráficos gerados com sucesso!")
