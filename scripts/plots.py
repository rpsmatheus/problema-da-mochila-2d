import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../resultados_stats.csv")

plt.figure(figsize=(10,6))

for metodo in df["Metodo"].unique():
    sub = df[df["Metodo"] == metodo]
    plt.plot(
        sub["N"],
        sub["Tempo_Medio"],
        marker="o",
        label=metodo
    )

plt.xlabel("Quantidade de Itens (N)")
plt.ylabel("Tempo Médio de Execução (s)")
plt.title("Crescimento do Tempo de Execução")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("tempo_vs_n.png")
plt.show()
