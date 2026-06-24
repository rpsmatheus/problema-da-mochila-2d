#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include "../headers/backtracking.h"

int *melhor_solucao = NULL;
int *solucao_atual = NULL;
int maior_lucro = 0;
bool timeout_atingido = false; // Flag para interromper a recursão

// Função recursiva com verificação de tempo
void mochila_backtracking(Item *itens, int indice_atual, int total_itens, 
                          int cap_peso, int cap_vol, 
                          int lucro_atual, int peso_atual, int vol_atual,
                          clock_t start_time) {

    // Verifica o timeout a cada 10.000 chamadas para não perder performance
    static int check_counter = 0;
    if (check_counter++ % 10000 == 0) {
        double elapsed = (double)(clock() - start_time) / CLOCKS_PER_SEC;
        if (elapsed > 3600.0) { // Limite de 1 hora
            timeout_atingido = true;
        }
    }

    // Se o timeout foi atingido, para de explorar novos galhos
    if (timeout_atingido) return;

    if (indice_atual == total_itens) {
        if (lucro_atual > maior_lucro) {
            maior_lucro = lucro_atual;
            for (int i = 0; i < total_itens; i++)
                melhor_solucao[i] = solucao_atual[i];
        }
        return;
    }

    // Tenta incluir o item atual (Verifica Peso E Volume)
    if (peso_atual + itens[indice_atual].weigh <= cap_peso && 
        vol_atual + itens[indice_atual].volume <= cap_vol) {
        
        solucao_atual[indice_atual] = 1;
        mochila_backtracking(itens, indice_atual + 1, total_itens, cap_peso, cap_vol,
                             lucro_atual + itens[indice_atual].value,
                             peso_atual + itens[indice_atual].weigh,
                             vol_atual + itens[indice_atual].volume,
                             start_time);
        solucao_atual[indice_atual] = 0;
    }

    // Tenta excluir o item atual
    mochila_backtracking(itens, indice_atual + 1, total_itens, cap_peso, cap_vol,
                         lucro_atual, peso_atual, vol_atual,
                         start_time);
}

void exibirResultadoBacktracking(Item *itens, int total_itens, int cap_p, int cap_v) {
    int peso_total = 0;
    int vol_total = 0;

    if (timeout_atingido) {
        printf("\n[AVISO] Tempo limite de 1h atingido! Exibindo melhor solucao encontrada ate agora.\n");
    }

    printf("Lucro máximo: R$ %d\n", maior_lucro);
    printf("Itens colocados na mochila:\n");
    for (int i = 0; i < total_itens; i++) {
        if (melhor_solucao[i]) {
            printf("\t(Item: %d, Valor: %d, Peso: %d, Volume: %d)\n", 
                    i + 1, itens[i].value, itens[i].weigh, itens[i].volume);
            peso_total += itens[i].weigh;
            vol_total += itens[i].volume;
        }
    }

    printf("Peso total: %d / %d\n", peso_total, cap_p);
    printf("Volume total: %d / %d\n", vol_total, cap_v);
}

int executarBacktracking(Backpack *mochila, clock_t start_time) {
    int total_itens = mochila->items_amount;
    
    melhor_solucao = (int*) calloc(total_itens, sizeof(int));
    solucao_atual = (int*) calloc(total_itens, sizeof(int));

    if (melhor_solucao == NULL || solucao_atual == NULL)
        return -1;

    maior_lucro = 0;
    timeout_atingido = false;

    // Inicia a recursão passando o tempo de início
    mochila_backtracking(mochila->items, 0, total_itens, 
                         mochila->weigh, mochila->volume, 
                         0, 0, 0,
                         start_time);

    exibirResultadoBacktracking(mochila->items, total_itens, mochila->weigh, mochila->volume);
    
    free(melhor_solucao);
    free(solucao_atual);

    return 0;
}