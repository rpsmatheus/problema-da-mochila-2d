#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV_SITE_PACKAGES = ROOT / "scripts" / "venv" / "lib" / "python3.12" / "site-packages"
if VENV_SITE_PACKAGES.exists():
    sys.path.insert(0, str(VENV_SITE_PACKAGES))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

try:
    import seaborn as sns
except ImportError:
    sns = None

INPUT = ROOT / "resultados_experimentos_stats.csv"
OUT_DIR = ROOT / "scripts"


def salvar_linha(df, eixo_x, filtro_coluna, filtro_valor, nome_arquivo, titulo, xlabel):
    subset = df[df[filtro_coluna] == filtro_valor].copy()
    if subset.empty:
        print(f"Pulando {nome_arquivo}: nao ha dados com {filtro_coluna}={filtro_valor}.")
        return

    plt.figure(figsize=(10, 6))
    for metodo in sorted(subset["Metodo"].unique()):
        dados = subset[subset["Metodo"] == metodo].sort_values(eixo_x)
        plt.plot(dados[eixo_x], dados["Tempo_Medio"], marker="o", label=metodo)

    plt.xlabel(xlabel)
    plt.ylabel("Tempo medio (s)")
    plt.title(titulo)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    caminho = OUT_DIR / nome_arquivo
    plt.savefig(caminho)
    plt.close()
    print(f"Grafico gerado: {caminho}")


def salvar_tempo_vs_n(df):
    combinacoes = df[["W", "V"]].drop_duplicates().sort_values(["W", "V"])
    if combinacoes.empty:
        return

    w = int(combinacoes.iloc[0]["W"])
    v = int(combinacoes.iloc[0]["V"])
    salvar_linha(
        df[(df["W"] == w) & (df["V"] == v)],
        "N",
        "W",
        w,
        "tempo_vs_n_menu.png",
        f"Tempo medio x quantidade de itens (W={w}, V={v})",
        "Quantidade de itens (N)",
    )


def salvar_tempo_vs_w(df):
    combinacoes = df[["N", "V"]].drop_duplicates().sort_values(["N", "V"])
    if combinacoes.empty:
        return

    n = int(combinacoes.iloc[0]["N"])
    v = int(combinacoes.iloc[0]["V"])
    subset = df[(df["N"] == n) & (df["V"] == v)]
    salvar_linha(
        subset,
        "W",
        "N",
        n,
        "tempo_vs_W_menu.png",
        f"Tempo medio x peso maximo (N={n}, V={v})",
        "Peso maximo (W)",
    )


def salvar_tempo_vs_v(df):
    combinacoes = df[["N", "W"]].drop_duplicates().sort_values(["N", "W"])
    if combinacoes.empty:
        return

    n = int(combinacoes.iloc[0]["N"])
    w = int(combinacoes.iloc[0]["W"])
    subset = df[(df["N"] == n) & (df["W"] == w)]
    salvar_linha(
        subset,
        "V",
        "N",
        n,
        "tempo_vs_V_menu.png",
        f"Tempo medio x volume maximo (N={n}, W={w})",
        "Volume maximo (V)",
    )


def salvar_heatmap_dynamic(df):
    dynamic = df[df["Metodo"] == "dynamic"].copy()
    if dynamic.empty:
        print("Pulando heatmap: nao ha dados do metodo dynamic.")
        return

    n_valores = sorted(dynamic["N"].unique())
    n = n_valores[0]
    subset = dynamic[dynamic["N"] == n]

    if subset["W"].nunique() < 2 or subset["V"].nunique() < 2:
        print("Pulando heatmap: e preciso ter pelo menos 2 valores de W e 2 valores de V.")
        return

    pivot = subset.pivot_table(index="W", columns="V", values="Tempo_Medio", aggfunc="mean")

    plt.figure(figsize=(8, 6))
    if sns is not None:
        sns.heatmap(pivot, annot=True, fmt=".5f", cmap="viridis")
    else:
        plt.imshow(pivot.values, aspect="auto")
        plt.colorbar(label="Tempo medio (s)")
        plt.xticks(range(len(pivot.columns)), pivot.columns)
        plt.yticks(range(len(pivot.index)), pivot.index)

    plt.title(f"Heatmap - Tempo medio dynamic (N={n})")
    plt.xlabel("Volume maximo (V)")
    plt.ylabel("Peso maximo (W)")
    plt.tight_layout()
    caminho = OUT_DIR / "heatmap_dynamic_menu.png"
    plt.savefig(caminho)
    plt.close()
    print(f"Grafico gerado: {caminho}")


def main():
    if not INPUT.exists():
        raise SystemExit(f"Arquivo nao encontrado: {INPUT}. Gere a tabela estatistica antes.")

    df = pd.read_csv(INPUT)
    df["Tempo_Medio"] = pd.to_numeric(df["Tempo_Medio"], errors="coerce")
    df = df.dropna(subset=["Tempo_Medio"])

    if df.empty:
        raise SystemExit("Tabela estatistica sem valores validos de Tempo_Medio.")

    salvar_tempo_vs_n(df)
    salvar_tempo_vs_w(df)
    salvar_tempo_vs_v(df)
    salvar_heatmap_dynamic(df)


if __name__ == "__main__":
    main()
