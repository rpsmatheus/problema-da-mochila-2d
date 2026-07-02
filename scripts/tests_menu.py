#!/usr/bin/env python3
import csv
import math
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "resultados_experimentos.csv"
OUTPUT = ROOT / "resultados_experimentos_testes.csv"
ALPHA = 0.05


def p_valor_teste_sinais(diferencas):
    diffs = [diff for diff in diferencas if diff != 0]
    n = len(diffs)
    if n == 0:
        return 1.0, 0, 0, 0

    positivos = sum(1 for diff in diffs if diff > 0)
    negativos = n - positivos
    extremo = min(positivos, negativos)

    probabilidade = sum(math.comb(n, k) for k in range(extremo + 1)) / (2 ** n)
    p_valor = min(1.0, 2 * probabilidade)
    return p_valor, n, positivos, negativos


def chave_instancia(valor):
    try:
        return int(valor)
    except ValueError:
        return valor


def comparar_metodos(grupo, metodo_a, metodo_b):
    tempos_a = {
        linha["Instancia"]: linha["Tempo"]
        for linha in grupo
        if linha["Metodo"] == metodo_a
    }
    tempos_b = {
        linha["Instancia"]: linha["Tempo"]
        for linha in grupo
        if linha["Metodo"] == metodo_b
    }

    pareado = [
        (tempos_a[instancia], tempos_b[instancia])
        for instancia in sorted(set(tempos_a) & set(tempos_b), key=chave_instancia)
    ]

    diferencas = [tempo_a - tempo_b for tempo_a, tempo_b in pareado]
    p_valor, pares_validos, a_mais_lento, b_mais_lento = p_valor_teste_sinais(diferencas)

    media_a = sum(tempo_a for tempo_a, _ in pareado) / len(pareado) if pareado else float("nan")
    media_b = sum(tempo_b for _, tempo_b in pareado) / len(pareado) if pareado else float("nan")

    if pares_validos == 0:
        resultado = "sem_dados"
        metodo_mais_rapido = ""
    elif p_valor >= ALPHA:
        resultado = "empate_estatistico"
        metodo_mais_rapido = ""
    elif media_a < media_b:
        resultado = "diferenca_significativa"
        metodo_mais_rapido = metodo_a
    else:
        resultado = "diferenca_significativa"
        metodo_mais_rapido = metodo_b

    return {
        "Metodo_A": metodo_a,
        "Metodo_B": metodo_b,
        "Pares_Validos": pares_validos,
        "Tempo_Medio_A": round(media_a, 5) if not math.isnan(media_a) else "",
        "Tempo_Medio_B": round(media_b, 5) if not math.isnan(media_b) else "",
        "A_Mais_Lento_Que_B": a_mais_lento,
        "B_Mais_Lento_Que_A": b_mais_lento,
        "P_Valor": round(p_valor, 5),
        "Alpha": ALPHA,
        "Resultado": resultado,
        "Metodo_Mais_Rapido": metodo_mais_rapido,
    }


def ler_grupos():
    grupos = {}
    with INPUT.open(newline="") as arquivo:
        reader = csv.DictReader(arquivo)
        for linha in reader:
            try:
                timeout = int(float(linha.get("Timeout", 0) or 0))
                tempo = float(linha["Tempo"])
                chave = (int(linha["N"]), int(linha["W"]), int(linha["V"]))
            except (KeyError, TypeError, ValueError):
                continue

            if timeout != 0:
                continue

            grupos.setdefault(chave, []).append({
                "Instancia": linha["Instancia"],
                "Metodo": linha["Metodo"],
                "Tempo": tempo,
            })
    return grupos


def main():
    if not INPUT.exists():
        raise SystemExit(f"Arquivo nao encontrado: {INPUT}")

    rows = []
    for (n, w, v), grupo in sorted(ler_grupos().items()):
        metodos = sorted({linha["Metodo"] for linha in grupo})
        for metodo_a, metodo_b in combinations(metodos, 2):
            row = {
                "N": n,
                "W": w,
                "V": v,
            }
            row.update(comparar_metodos(grupo, metodo_a, metodo_b))
            rows.append(row)

    colunas = [
        "N", "W", "V", "Metodo_A", "Metodo_B", "Pares_Validos",
        "Tempo_Medio_A", "Tempo_Medio_B", "A_Mais_Lento_Que_B",
        "B_Mais_Lento_Que_A", "P_Valor", "Alpha", "Resultado",
        "Metodo_Mais_Rapido",
    ]
    with OUTPUT.open("w", newline="") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=colunas)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Testes estatisticos gerados em: {OUTPUT}")


if __name__ == "__main__":
    main()
