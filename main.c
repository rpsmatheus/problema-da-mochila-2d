#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <time.h> // Adicionado para lidar com o tempo

#include "headers/i_o.h"
#include "headers/dynamic.h"
#include "headers/structures.h"
#include "headers/backtracking.h"
#include "headers/bnb.h"

bool hasEnoughArguments(int argc)
{
    return argc == 3;
}

int main(int argc, char *argv[])
{
    FILE *file;
    Backpack backpack;
    unsigned int lines_amount;
    clock_t start_time; // Variável para armazenar o tempo inicial

    if(hasEnoughArguments(argc) == false)
    {
        printf("Quantidade errada de argumentos!\n\n");
        printf("Uso: %s <nome_arquivo> <dynamic | backtracking | bnb>\n", argv[0]);
        exit(1);
    }

    file = openFile(argv[1], "r");

    if(file == NULL)
    {
        printf("Falha ao abrir o arquivo!\n");
        exit(2);
    }

    lines_amount = countLines(file);
    backpack.items = allocItems(lines_amount - 1);
    readBackpackDataFile(file, lines_amount, &backpack);

    // Captura o tempo EXATO antes de iniciar o algoritmo selecionado
    start_time = clock();

    // Seleção do método passando o start_time para controle de timeout
    if(!strcmp(argv[2], "dynamic")) {
        printf("Executando Dynamic Programming (Limite 2h)...\n");
        dynamicApproch(&backpack, start_time);
    }
    else if(!strcmp(argv[2], "backtracking")) {
        printf("Executando Backtracking (Limite 2h)...\n");
        executarBacktracking(&backpack, start_time);
    }
    else if(!strcmp(argv[2], "bnb")) {
        printf("Executando Branch and Bound (Limite 2h)...\n");
        branchAndBoundApproach(&backpack, start_time);
    }
    else {
        printf("Metodo desconhecido: %s\n", argv[2]);
    }

    // Calcula e imprime o tempo total de execução no final
    double time_taken = (double)(clock() - start_time) / CLOCKS_PER_SEC;
    printf("\nTempo de execucao: %.4fs\n", time_taken);

    // Cleanup
    freeItems(&backpack.items);
    closeFile(file);

    return 0;
}