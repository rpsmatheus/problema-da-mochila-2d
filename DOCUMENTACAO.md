# Documentacao do Sistema - Mochila 2D

Este projeto implementa e compara tres abordagens para o problema da mochila com duas restricoes: peso e volume.

Os algoritmos implementados sao:

- Programacao Dinamica (`dynamic`)
- Backtracking (`backtracking`)
- Branch and Bound (`bnb`)

O sistema tambem possui gerador de instancias, menu interativo, execucao automatica de experimentos e geracao de tabelas em CSV.

## 1. Estrutura do Projeto

```text
PAA-TP1-25.2/
├── main.c
├── Makefile
├── menu.py
├── DOCUMENTACAO.md
├── headers/
├── src/
├── input_files/
├── app/
├── build/
├── scripts/
├── tst/
├── results/
├── resultados_experimentos.csv
└── resultados_experimentos_stats.csv
```

## 2. Principais Arquivos e Pastas

### `main.c`

Arquivo principal do programa em C. Ele recebe dois argumentos:

```bash
./app/exe <arquivo_instancia> <dynamic | backtracking | bnb>
```

Ele abre a instancia, le os dados da mochila e chama o algoritmo escolhido.

### `src/`

Contem as implementacoes dos algoritmos e funcoes auxiliares.

```text
src/dynamic.c        -> Programacao Dinamica
src/backtracking.c   -> Backtracking
src/bnb.c            -> Branch and Bound
src/i_o.c            -> leitura dos arquivos de instancia
src/structures.c     -> alocacao/liberacao de estruturas
```

### `headers/`

Contem os arquivos `.h` com as declaracoes usadas pelos arquivos `.c`.

```text
headers/dynamic.h
headers/backtracking.h
headers/bnb.h
headers/i_o.h
headers/structures.h
```

### `input_files/`

Contem o gerador de instancias e as instancias geradas.

```text
input_files/instance_generator.c  -> codigo fonte do gerador
input_files/generator             -> executavel do gerador
input_files/instancia_*.txt        -> instancias geradas
```

### `app/`

Contem o executavel principal compilado:

```text
app/exe
```

### `build/`

Contem arquivos objeto `.o` gerados pela compilacao. Nao e necessario editar manualmente.

### `scripts/`

Contem scripts Python auxiliares para benchmarks, estatisticas e graficos.

```text
scripts/stats_menu.py    -> gera tabela estatistica a partir do CSV do menu
scripts/benchmark.py     -> benchmark alternativo variando N
scripts/benchmark_mv.py  -> benchmark alternativo variando W e V
scripts/stats.py         -> estatisticas do benchmark.py
scripts/stats_mv.py      -> estatisticas do benchmark_mv.py
scripts/plots.py         -> graficos do benchmark.py
scripts/plots_mv.py      -> graficos do benchmark_mv.py
scripts/venv/            -> ambiente/pacotes Python usados por pandas, scipy etc.
```

### `menu.py`

Menu interativo principal do projeto. E o jeito mais simples de compilar, gerar instancias, rodar algoritmos, rodar experimentos e gerar tabela.

## 3. Formato das Instancias

Cada arquivo de instancia tem o seguinte formato:

```text
W V
peso_1 volume_1 valor_1
peso_2 volume_2 valor_2
...
peso_n volume_n valor_n
```

Exemplo:

```text
100 100
24 79 335
75 64 884
6 26 428
```

A primeira linha informa:

```text
capacidade de peso W
capacidade de volume V
```

Cada linha seguinte informa um item:

```text
peso volume valor
```

## 4. Como Compilar

Entre na raiz do projeto:

```bash
cd /home/usuario/Downloads/PAA-TP1-25.2
```

Para limpar compilacoes antigas:

```bash
make clean
```

Para compilar o programa principal:

```bash
make
```

Isso gera:

```text
app/exe
```

Para compilar o gerador de instancias:

```bash
make gen
```

Isso gera:

```text
input_files/generator
```

Fluxo completo recomendado:

```bash
cd /home/usuario/Downloads/PAA-TP1-25.2
make clean
make
make gen
```

## 5. Como Usar o Menu

Execute:

```bash
cd /home/usuario/Downloads/PAA-TP1-25.2
python3 menu.py
```

O menu mostra:

```text
1 - Compilar tudo
2 - Rodar experimentos e gerar CSV
3 - Gerar tabela estatistica do CSV
4 - Gerar graficos da tabela estatistica
5 - Gerar 10 instancias para uma combinacao
6 - Rodar Programacao Dinamica
7 - Rodar Backtracking
8 - Rodar Branch and Bound
0 - Sair
```

### Opcao 1 - Compilar tudo

Executa:

```bash
make
make gen
```

Ou seja, compila:

```text
app/exe
input_files/generator
```

### Opcao 2 - Rodar experimentos e gerar CSV

Esta opcao pede listas de valores para:

```text
N -> quantidade de itens
W -> peso maximo da mochila
V -> volume maximo da mochila
```

Exemplo de entrada:

```text
N: 100, 200, 300
W: 100, 200, 300
V: 100, 200, 300
```

O sistema faz automaticamente:

```text
para cada combinacao N x W x V:
    gera 10 instancias
    para cada instancia:
        roda dynamic
        roda backtracking
        roda bnb
        salva os resultados no CSV
```

No exemplo acima:

```text
3 valores de N x 3 valores de W x 3 valores de V = 27 combinacoes
27 combinacoes x 10 instancias = 270 instancias
270 instancias x 3 algoritmos = 810 execucoes
```

O CSV gerado e:

```text
resultados_experimentos.csv
```

Colunas do CSV:

```text
N,W,V,Instancia,Metodo,Lucro,Tempo,Timeout
```

### Opcao 3 - Gerar tabela estatistica do CSV

Le o arquivo:

```text
resultados_experimentos.csv
```

e gera:

```text
resultados_experimentos_stats.csv
```

Essa tabela agrupa os resultados por:

```text
N, W, V, Metodo
```

e calcula:

```text
Execucoes
Execucoes_Validas
Timeouts
Timeout_%
Lucro_Medio
Tempo_Medio
Tempo_Desvio_Padrao
Tempo_IC_95
```

O script usado e:

```text
scripts/stats_menu.py
```

Esse script usa `pandas`.

### Opcao 4 - Gerar graficos da tabela estatistica

Le o arquivo:

```text
resultados_experimentos_stats.csv
```

e gera os graficos:

```text
scripts/tempo_vs_n_menu.png
scripts/tempo_vs_W_menu.png
scripts/tempo_vs_V_menu.png
scripts/heatmap_dynamic_menu.png
```

O script usado e:

```text
scripts/plots_menu.py
```

Antes de usar essa opcao, gere a tabela estatistica pela opcao 3.

### Opcao 5 - Gerar 10 instancias para uma combinacao

Pede apenas um valor para cada parametro:

```text
N
W
V
```

Exemplo:

```text
N = 200
W = 1000
V = 1000
```

Gera 10 arquivos:

```text
input_files/instancia_n200_W1000_V1000_i1.txt
input_files/instancia_n200_W1000_V1000_i2.txt
...
input_files/instancia_n200_W1000_V1000_i10.txt
```

### Opcoes 6, 7 e 8 - Rodar apenas um algoritmo

Opcoes:

```text
6 - Programacao Dinamica
7 - Backtracking
8 - Branch and Bound
```

O menu pede o nome ou caminho da instancia. Pode digitar apenas o nome:

```text
instancia_n100_W100_V100_i1.txt
```

O menu procura automaticamente em:

```text
raiz do projeto
input_files/
```

Tambem aceita caminho completo:

```text
input_files/instancia_n100_W100_V100_i1.txt
```

## 6. Como Gerar Instancias Manualmente

Compile o gerador:

```bash
make gen
```

Depois rode:

```bash
cd input_files
./generator <N> <W> <V>
```

Exemplo:

```bash
cd /home/usuario/Downloads/PAA-TP1-25.2/input_files
./generator 200 1000 1000
```

Isso gera 10 arquivos automaticamente:

```text
instancia_n200_W1000_V1000_i1.txt
instancia_n200_W1000_V1000_i2.txt
...
instancia_n200_W1000_V1000_i10.txt
```

O gerador tambem aceita uma seed opcional:

```bash
./generator 200 1000 1000 12345
```

Usar seed permite reproduzir as mesmas instancias depois.

## 7. Como Rodar um Algoritmo Manualmente

Depois de compilar:

```bash
make
```

Use:

```bash
./app/exe <arquivo_instancia> <metodo>
```

Metodos validos:

```text
dynamic
backtracking
bnb
```

Exemplos:

```bash
./app/exe input_files/instancia_n100_W100_V100_i1.txt dynamic
./app/exe input_files/instancia_n100_W100_V100_i1.txt backtracking
./app/exe input_files/instancia_n100_W100_V100_i1.txt bnb
```

A saida mostra:

```text
lucro maximo
itens escolhidos
peso total
volume total
tempo de execucao
```

## 8. Como Gerar as Tabelas

### Pelo menu

Fluxo recomendado:

```bash
python3 menu.py
```

1. Escolha `2` para rodar experimentos e gerar:

```text
resultados_experimentos.csv
```

2. Depois escolha `3` para gerar:

```text
resultados_experimentos_stats.csv
```

3. Depois escolha `4` para gerar os graficos:

```text
scripts/tempo_vs_n_menu.png
scripts/tempo_vs_W_menu.png
scripts/tempo_vs_V_menu.png
scripts/heatmap_dynamic_menu.png
```

### Pelo terminal

Depois de gerar `resultados_experimentos.csv`, rode:

```bash
/usr/bin/python3.12 scripts/stats_menu.py
```

Isso gera:

```text
resultados_experimentos_stats.csv
```

## 9. Sobre o `pandas` e o `scripts/venv`

O script de estatisticas usa `pandas`.

As bibliotecas Python estao em:

```text
scripts/venv/lib/python3.12/site-packages
```

Nessa pasta existem pacotes como:

```text
pandas
numpy
scipy
matplotlib
seaborn
```

Observacao: o ambiente `scripts/venv` esta incompleto porque nao possui o executavel:

```text
scripts/venv/bin/python
```

Por isso, o script `stats_menu.py` adiciona automaticamente o caminho `site-packages` ao `sys.path` e deve ser executado com:

```bash
/usr/bin/python3.12 scripts/stats_menu.py
```

O menu ja faz isso automaticamente na opcao 3.

## 10. Timeouts

O limite de tempo por execucao esta configurado como:

```text
1 hora = 3600 segundos
```

Esse limite vale para:

```text
Programacao Dinamica
Backtracking
Branch and Bound
Menu/experimentos
```

Se um algoritmo ultrapassar esse limite, o CSV marca `Timeout = 1`.

## 11. Observacoes Sobre o Backtracking

O backtracking pode demorar muito para valores grandes de `N`, principalmente `N >= 100`.

Isso acontece porque o backtracking explora uma arvore de decisoes de incluir/excluir itens. Mesmo com podas por peso e volume, o numero de combinacoes pode crescer muito.

Para testes rapidos, use valores menores:

```text
N: 10, 20, 30
W: 100
V: 100
```

Para experimentos maiores, o backtracking pode levar bastante tempo, especialmente com timeout de 1 hora.

## 12. Branch and Bound

O Branch and Bound foi ajustado para gerar uma solucao inicial gulosa antes de iniciar a busca.

Isso evita comecar as comparacoes com solucao vazia quando existe algum item viavel.

O algoritmo:

1. ordena os itens por eficiencia valor/peso;
2. gera uma solucao inicial viavel respeitando peso e volume;
3. usa essa solucao como melhor solucao inicial;
4. executa a busca Branch and Bound.

## 13. Gerador de Instancias

O gerador atual cria sempre 10 instancias para cada combinacao `N, W, V`.

Para cada item, ele gera:

```text
peso   entre 1 e W
volume entre 1 e V
valor  entre 1 e 1000
```

Os arquivos sao salvos no formato:

```text
instancia_n<N>_W<W>_V<V>_i<id>.txt
```

Exemplo:

```text
instancia_n200_W1000_V1000_i1.txt
```

## 14. Arquivos de Resultado

### `resultados_experimentos.csv`

Tabela bruta gerada pelo menu na opcao 2.

Cada linha representa uma execucao de um algoritmo em uma instancia.

Colunas:

```text
N,W,V,Instancia,Metodo,Lucro,Tempo,Timeout
```

### `resultados_experimentos_stats.csv`

Tabela estatistica gerada pela opcao 3 do menu.

Cada linha representa o resumo de um metodo para uma combinacao `N, W, V`.

Colunas:

```text
N,W,V,Metodo,Execucoes,Execucoes_Validas,Timeouts,Timeout_%,Lucro_Medio,Tempo_Medio,Tempo_Desvio_Padrao,Tempo_IC_95
```

## 15. Comandos Mais Usados

Compilar tudo manualmente:

```bash
make clean
make
make gen
```

Abrir o menu:

```bash
python3 menu.py
```

Gerar 10 instancias manualmente:

```bash
cd input_files
./generator 100 100 100
cd ..
```

Rodar um algoritmo manualmente:

```bash
./app/exe input_files/instancia_n100_W100_V100_i1.txt dynamic
```

Gerar tabela estatistica manualmente:

```bash
/usr/bin/python3.12 scripts/stats_menu.py
```

Gerar graficos manualmente:

```bash
/usr/bin/python3.12 scripts/plots_menu.py
```

## 16. Fluxo Recomendado Para o Trabalho

1. Entrar na pasta do projeto:

```bash
cd /home/usuario/Downloads/PAA-TP1-25.2
```

2. Abrir o menu:

```bash
python3 menu.py
```

3. Escolher opcao `1` para compilar tudo.

4. Escolher opcao `2` para rodar os experimentos.

5. Informar os valores desejados de `N`, `W` e `V`.

6. Esperar o CSV bruto ser gerado:

```text
resultados_experimentos.csv
```

7. Escolher opcao `3` para gerar a tabela estatistica:

```text
resultados_experimentos_stats.csv
```

8. Escolher opcao `4` para gerar os graficos:

```text
scripts/tempo_vs_n_menu.png
scripts/tempo_vs_W_menu.png
scripts/tempo_vs_V_menu.png
scripts/heatmap_dynamic_menu.png
```

9. Usar os CSVs e graficos gerados no relatorio do trabalho.
