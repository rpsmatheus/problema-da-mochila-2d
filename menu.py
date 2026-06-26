#!/usr/bin/env python3
import csv
import os
import subprocess
import time
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input_files"
EXEC = ROOT / "app" / "exe"
GEN = INPUT_DIR / "generator"
CSV_EXPERIMENTOS = ROOT / "resultados_experimentos.csv"
STATS_MENU = ROOT / "scripts" / "stats_menu.py"
PLOTS_MENU = ROOT / "scripts" / "plots_menu.py"
INSTANCES_PER_COMBINATION = 10
METHODS = ["dynamic", "backtracking", "bnb"]
TIMEOUT = 7200


def parse_lista_inteiros(texto):
    valores = texto.replace(",", " ").split()
    if not valores:
        raise ValueError("nenhum valor informado")

    numeros = []
    for valor in valores:
        numero = int(valor)
        if numero <= 0:
            raise ValueError("os valores devem ser positivos")
        numeros.append(numero)

    return numeros


def pedir_lista(label):
    while True:
        texto = input(f"Digite os valores de {label} separados por virgula ou espaco: ").strip()
        try:
            return parse_lista_inteiros(texto)
        except ValueError as erro:
            print(f"Entrada invalida: {erro}")


def pedir_inteiro(label):
    while True:
        texto = input(f"Digite {label}: ").strip()
        try:
            valor = int(texto)
            if valor <= 0:
                raise ValueError
            return valor
        except ValueError:
            print("Entrada invalida. Digite um numero inteiro positivo.")


def compilar_tudo():
    print("\nCompilando programa principal...")
    subprocess.run(["make"], cwd=ROOT, check=True)

    print("\nCompilando gerador de instancias...")
    subprocess.run(["make", "gen"], cwd=ROOT, check=True)

    print("\nCompilacao concluida.")


def garantir_binarios():
    faltando = []
    if not EXEC.exists():
        faltando.append(str(EXEC))
    if not GEN.exists():
        faltando.append(str(GEN))

    if faltando:
        print("\nBinarios ausentes:")
        for item in faltando:
            print(f"- {item}")
        print("Compile antes pela opcao 1 do menu.")
        return False

    return True


def gerar_instancias(n, w, v):
    subprocess.run(
        [str(GEN), str(n), str(w), str(v)],
        cwd=INPUT_DIR,
        check=True
    )


def limpar_instancias():
    print(f"\nProcurando instancias antigas em {INPUT_DIR}...")
    apagados = 0
    for arquivo in INPUT_DIR.glob("*.txt"):
        try:
            arquivo.unlink()
            apagados += 1
        except Exception as e:
            print(f"Erro ao apagar {arquivo.name}: {e}")
    
    print(f"Limpeza concluida! {apagados} arquivo(s) .txt apagado(s) com sucesso.")


def caminho_instancia(n, w, v, instance_id):
    return INPUT_DIR / f"instancia_n{n}_W{w}_V{v}_i{instance_id}.txt"


def extrair_lucro(stdout):
    for linha in stdout.splitlines():
        if "Lucro máximo" in linha:
            return float(linha.split("R$")[1].strip())
    return None


def rodar_algoritmo(instancia, metodo, mostrar_saida=False):
    inicio = time.time()
    try:
        resultado = subprocess.run(
            [str(EXEC), str(instancia), metodo],
            cwd=ROOT,
            capture_output=not mostrar_saida,
            text=True,
            timeout=TIMEOUT
        )
        tempo = time.time() - inicio

        if mostrar_saida:
            return None, tempo, False

        lucro = extrair_lucro(resultado.stdout)
        return lucro, tempo, False

    except subprocess.TimeoutExpired:
        return None, TIMEOUT, True


def rodar_experimentos(ignorar_bt=False):
    if not garantir_binarios():
        return

    ns = pedir_lista("quantidade de itens N. Ex: 100, 200, 300")
    ws = pedir_lista("pesos maximos W. Ex: 100, 200, 300")
    vs = pedir_lista("volumes maximos V. Ex: 100, 200, 300")

    # Filtra os métodos caso a opção 9 tenha sido escolhida
    metodos_execucao = ["dynamic", "bnb"] if ignorar_bt else METHODS
    
    total = len(ns) * len(ws) * len(vs) * INSTANCES_PER_COMBINATION * len(metodos_execucao)
    atual = 0

    print(f"\nTotal de execucoes: {total}")
    print(f"CSV de saida: {CSV_EXPERIMENTOS}\n")

    file_exists = CSV_EXPERIMENTOS.exists()
    mode = "a" if file_exists else "w"

    with CSV_EXPERIMENTOS.open(mode, newline="") as arquivo:
        writer = csv.writer(arquivo)
        
        # Escreve o cabeçalho apenas se o arquivo for novo
        if not file_exists:
            writer.writerow([
                "N", "W", "V", "Instancia", "Metodo",
                "Lucro", "Tempo", "Timeout"
            ])

        for n in ns:
            for w in ws:
                for v in vs:
                    print(f"\nGerando 10 instancias para N={n}, W={w}, V={v}")
                    gerar_instancias(n, w, v)

                    for instance_id in range(1, INSTANCES_PER_COMBINATION + 1):
                        instancia = caminho_instancia(n, w, v, instance_id)

                        for metodo in metodos_execucao:
                            atual += 1
                            print(
                                f"[{atual}/{total}] "
                                f"N={n} W={w} V={v} instancia={instance_id}/10 metodo={metodo}",
                                flush=True
                            )

                            lucro, tempo, timeout = rodar_algoritmo(instancia, metodo)
                            writer.writerow([
                                n, w, v, instance_id, metodo,
                                f"{lucro:.5f}" if lucro is not None else "",
                                f"{tempo:.5f}",
                                int(timeout)
                            ])
                            arquivo.flush()

    print(f"\nExperimentos finalizados. CSV salvo em: {CSV_EXPERIMENTOS}")


def gerar_tabela_estatistica():
    if not CSV_EXPERIMENTOS.exists():
        print(f"CSV nao encontrado: {CSV_EXPERIMENTOS}")
        print("Rode os experimentos pela opcao 2 antes de gerar a tabela.")
        return

    subprocess.run(["/usr/bin/python3.12", str(STATS_MENU)], cwd=ROOT, check=True)


def gerar_graficos():
    stats_file = ROOT / "resultados_experimentos_stats.csv"
    if not stats_file.exists():
        print(f"Tabela estatistica nao encontrada: {stats_file}")
        print("Gere a tabela pela opcao 3 antes de gerar os graficos.")
        return

    subprocess.run(["/usr/bin/python3.12", str(PLOTS_MENU)], cwd=ROOT, check=True)


def gerar_uma_combinacao():
    if not garantir_binarios():
        return

    n = pedir_inteiro("a quantidade de itens N")
    w = pedir_inteiro("o peso maximo W")
    v = pedir_inteiro("o volume maximo V")

    print(f"\nGerando 10 instancias para N={n}, W={w}, V={v}...")
    gerar_instancias(n, w, v)
    print(f"\nArquivos gerados em: {INPUT_DIR}")
    for i in range(1, INSTANCES_PER_COMBINATION + 1):
        print(caminho_instancia(n, w, v, i).name)


def pedir_caminho_instancia():
    texto = input("Digite o caminho ou nome da instancia: ").strip()
    caminho = Path(texto)

    if caminho.is_absolute():
        candidatos = [caminho]
    else:
        candidatos = [
            ROOT / caminho,
            INPUT_DIR / caminho,
        ]

    for candidato in candidatos:
        if candidato.exists():
            return candidato

    print("Arquivo nao encontrado. Caminhos verificados:")
    for candidato in candidatos:
        print(f"- {candidato}")
    return None


def extrair_dados_arquivo(nome_arquivo):
    match = re.search(r"instancia_n(\d+)_W(\d+)_V(\d+)_i(\d+)\.txt", nome_arquivo)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4))
    return None, None, None, None


def rodar_um_metodo(metodo):
    if not garantir_binarios():
        return

    instancia = pedir_caminho_instancia()
    if instancia is None:
        return

    print(f"\nRodando {metodo} em {instancia}...\n")
    lucro, tempo, timeout = rodar_algoritmo(instancia, metodo, mostrar_saida=True)
    if timeout:
        print(f"\nTimeout de {TIMEOUT}s atingido.")

    salvar = input("\nDeseja salvar esse resultado automaticamente no CSV? (s/n): ").strip().lower()
    if salvar == 's':
        n, w, v, inst_id = extrair_dados_arquivo(instancia.name)
        if n is not None:
            file_exists = CSV_EXPERIMENTOS.exists()
            with CSV_EXPERIMENTOS.open("a", newline="") as arquivo:
                writer = csv.writer(arquivo)
                if not file_exists:
                    writer.writerow(["N", "W", "V", "Instancia", "Metodo", "Lucro", "Tempo", "Timeout"])
                writer.writerow([
                    n, w, v, inst_id, metodo,
                    f"{lucro:.5f}" if lucro is not None and not timeout else "",
                    f"{tempo:.5f}",
                    int(timeout)
                ])
            print("✅ Resultado salvo com sucesso no CSV!")
        else:
            print("❌ Erro: O nome do arquivo não segue o padrão gerado. Não foi possível extrair os dados para o CSV.")


def menu():
    while True:
        print("\n========== MENU ==========")
        print("1 - Compilar tudo")
        print("2 - Rodar experimentos e gerar CSV (Os 3 algoritmos)")
        print("3 - Gerar tabela estatistica do CSV")
        print("4 - Gerar graficos da tabela estatistica")
        print("5 - Gerar 10 instancias para uma combinacao")
        print("6 - Rodar Programacao Dinamica")
        print("7 - Rodar Backtracking")
        print("8 - Rodar Branch and Bound")
        print("9 - Rodar experimentos (SEM Backtracking)")
        print("10 - Limpar instancias antigas (.txt)")
        print("0 - Sair")

        opcao = input("Escolha uma opcao: ").strip()

        try:
            if opcao == "1":
                compilar_tudo()
            elif opcao == "2":
                rodar_experimentos(ignorar_bt=False)
            elif opcao == "3":
                gerar_tabela_estatistica()
            elif opcao == "4":
                gerar_graficos()
            elif opcao == "5":
                gerar_uma_combinacao()
            elif opcao == "6":
                rodar_um_metodo("dynamic")
            elif opcao == "7":
                rodar_um_metodo("backtracking")
            elif opcao == "8":
                rodar_um_metodo("bnb")
            elif opcao == "9":
                rodar_experimentos(ignorar_bt=True)
            elif opcao == "10":
                limpar_instancias()
            elif opcao == "0":
                print("Saindo.")
                break
            else:
                print("Opcao invalida.")
        except subprocess.CalledProcessError as erro:
            print(f"Comando falhou com codigo {erro.returncode}.")
        except KeyboardInterrupt:
            print("\nOperacao interrompida.")


if __name__ == "__main__":
    menu()