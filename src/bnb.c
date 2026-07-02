#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>
#include "../headers/bnb.h"


static bool *best_items = NULL;
static int best_weight = 0;
static int best_volume = 0;
static int *order_by_weight = NULL;
static int *order_by_volume = NULL;
static Item *items_for_bound = NULL;
static int selected_words = 0;
static bool timeout_bnb = false;

// Função de comparação para ordenar os itens com base na eficiência (valor / (peso + volume))
int compararItensEficiencia(const void *a, const void *b) {
    Item *i1 = (Item *)a;
    Item *i2 = (Item *)b;
    double r1 = (double)i1->value / (i1->weigh + i1->volume);
    double r2 = (double)i2->value / (i2->weigh + i2->volume);
    if (r1 < r2) return 1;
    if (r1 > r2) return -1;
    return 0;
}


static void copyBestItemsFromBits(unsigned long long *selected, int items_amount) {
    for (int i = 0; i < items_amount; i++)
        best_items[i] = (selected[i / 64] & (1ULL << (i % 64))) != 0;
}

static void setBit(unsigned long long *selected, int index) {
    selected[index / 64] |= 1ULL << (index % 64);
}

static void clearBit(unsigned long long *selected, int index) {
    selected[index / 64] &= ~(1ULL << (index % 64));
}

// Função para calcular a razão valor/peso ou valor/volume para um item específico
static double ratioForOrder(int index, bool use_weight) {
    Item *item = &items_for_bound[index];

    // Se use_weight for verdadeiro, usamos o peso; caso contrário, usamos o volume
    int capacity_use = use_weight ? item->weigh : item->volume;

    // Se a capacidade usada for zero, retornamos infinito para evitar divisão por zero
    if (capacity_use <= 0)
        return INFINITY;

    return (double)item->value / capacity_use;
}

// Funções de comparação para ordenar os índices dos itens com base na razão valor/peso ou valor/volume
static int compareWeightOrder(const void *a, const void *b) {
    int ia = *(const int *)a;
    int ib = *(const int *)b;
    double ra = ratioForOrder(ia, true);
    double rb = ratioForOrder(ib, true);

    if (ra < rb) return 1;
    if (ra > rb) return -1;
    return 0;
}

static int compareVolumeOrder(const void *a, const void *b) {
    int ia = *(const int *)a;
    int ib = *(const int *)b;
    double ra = ratioForOrder(ia, false);
    double rb = ratioForOrder(ib, false);

    if (ra < rb) return 1;
    if (ra > rb) return -1;
    return 0;
}

// cria e ordena os arrays de índices dos itens com base na razão valor/peso e valor/volume
static int buildBoundOrders(Backpack *b) {
    order_by_weight = malloc(b->items_amount * sizeof(int));
    order_by_volume = malloc(b->items_amount * sizeof(int));

    if (order_by_weight == NULL || order_by_volume == NULL) {
        free(order_by_weight);
        free(order_by_volume);
        order_by_weight = NULL;
        order_by_volume = NULL;
        return -1;
    }

    items_for_bound = b->items;
    for (int i = 0; i < b->items_amount; i++) {
        order_by_weight[i] = i;
        order_by_volume[i] = i;
    }

    qsort(order_by_weight, b->items_amount, sizeof(int), compareWeightOrder);
    qsort(order_by_volume, b->items_amount, sizeof(int), compareVolumeOrder);
    return 0;
}

static void freeBoundOrders() {
    free(order_by_weight);
    free(order_by_volume);
    order_by_weight = NULL;
    order_by_volume = NULL;
    items_for_bound = NULL;
}

// Função para calcular o bound relaxado considerando peso ou volume
static float calculateRelaxedBound(Node *node, Backpack *b, bool use_weight) {
    int remaining_capacity;
    int *order = use_weight ? order_by_weight : order_by_volume;

    // Calcula a capacidade restante com base no peso ou volume
    if (use_weight)
        remaining_capacity = b->weigh - node->weight;
    else
        remaining_capacity = b->volume - node->volume;

    if (remaining_capacity < 0)
        return 0.0f;

    float bound = node->profit;

    // Itera sobre os itens ordenados e adiciona-os ao bound relaxado até que a capacidade restante seja preenchida
    for (int i = 0; i < b->items_amount && remaining_capacity > 0; i++) {
        int item_index = order[i];

        if (item_index <= node->level)
            continue;

        Item *item = &b->items[item_index];
        int capacity_use = use_weight ? item->weigh : item->volume;

        if (capacity_use <= remaining_capacity) {
            remaining_capacity -= capacity_use;
            bound += item->value;
        } else if (capacity_use > 0) {
            bound += item->value * ((float)remaining_capacity / capacity_use);
            remaining_capacity = 0;
        }
    }

    return bound;
}

/* =========================================================
   BOUND ADMISSÍVEL COM PESO E VOLUME
   ========================================================= */

float calculateBound(Node *node, Backpack *b) {

    if (node->weight > b->weigh || node->volume > b->volume)
        return 0;

    float weight_bound = calculateRelaxedBound(node, b, true);
    float volume_bound = calculateRelaxedBound(node, b, false);

    return fminf(weight_bound, volume_bound);
}

/* =========================================================
   SOLUÇÃO INICIAL GULOSA
   ========================================================= */

int generateInitialSolution(Backpack *b) {
    int initial_profit = 0;

    best_weight = 0;
    best_volume = 0;

    for (int i = 0; i < b->items_amount; i++) {
        int next_weight = best_weight + b->items[i].weigh;
        int next_volume = best_volume + b->items[i].volume;

        if (next_weight <= b->weigh && next_volume <= b->volume) {
            best_items[i] = true;
            best_weight = next_weight;
            best_volume = next_volume;
            initial_profit += b->items[i].value;
        }
    }

    return initial_profit;
}

static void branchAndBoundDfs(Backpack *b, int level, int weight, int volume,
                              int profit, unsigned long long *selected,
                              int *best_profit, clock_t start_time) {
    static int check_counter = 0;

    if (check_counter++ % 10000 == 0) {
        double elapsed = (double)(clock() - start_time) / CLOCKS_PER_SEC;
        if (elapsed > 7200.0) {
            timeout_bnb = true;
            return;
        }
    }

    if (timeout_bnb)
        return;

    Node partial;
    partial.level = level - 1;
    partial.weight = weight;
    partial.volume = volume;
    partial.profit = profit;
    partial.bound = 0.0f;
    partial.selected_items = selected;

    if (calculateBound(&partial, b) < *best_profit)
        return;

    if (level >= b->items_amount)
        return;

    Item *item = &b->items[level];
    int next_weight = weight + item->weigh;
    int next_volume = volume + item->volume;
    int next_profit = profit + item->value;

    if (next_weight <= b->weigh && next_volume <= b->volume) {
        setBit(selected, level);

        if (next_profit > *best_profit) {
            *best_profit = next_profit;
            best_weight = next_weight;
            best_volume = next_volume;
            copyBestItemsFromBits(selected, b->items_amount);
        }

        branchAndBoundDfs(b, level + 1, next_weight, next_volume,
                          next_profit, selected, best_profit, start_time);
        clearBit(selected, level);
    }

    branchAndBoundDfs(b, level + 1, weight, volume, profit,
                      selected, best_profit, start_time);
}

/* =========================================================
   BRANCH AND BOUND
   ========================================================= */

int branchAndBoundApproach(Backpack *b, clock_t start_time) {

    printf("Executando Branch and Bound (Limite 2h)...\n");

    qsort(b->items, b->items_amount, sizeof(Item),
          compararItensEficiencia);

    selected_words = (b->items_amount + 63) / 64;

    if (buildBoundOrders(b) != 0) {
        printf("Erro: Falha de memoria ao preparar bounds do BnB.\n");
        return -1;
    }

    int best_profit = 0;
    best_items = calloc(b->items_amount, sizeof(bool));
    best_profit = generateInitialSolution(b);

    unsigned long long *selected = calloc(selected_words, sizeof(unsigned long long));
    if (selected == NULL) {
        printf("Erro: Falha de memoria ao preparar selecao do BnB.\n");
        free(best_items);
        freeBoundOrders();
        return -1;
    }

    timeout_bnb = false;
    branchAndBoundDfs(b, 0, 0, 0, 0, selected, &best_profit, start_time);

    if (timeout_bnb) {
        printf("\n[TIMEOUT] Branch and Bound atingiu 2h! Exibindo melhor solucao encontrada ate agora.\n");
    }

    free(selected);

    printf("Lucro máximo: R$ %d\n", best_profit);
    printf("Itens colocados na mochila:\n");

    for (int i = 0; i < b->items_amount; i++) {
        if (best_items[i]) {
            printf("\t(Item: %d, Valor: %d, Peso: %d, Volume: %d)\n",
                   i + 1,
                   b->items[i].value,
                   b->items[i].weigh,
                   b->items[i].volume);
        }
    }

    printf("Peso total: %d / %d\n", best_weight, b->weigh);
    printf("Volume total: %d / %d\n", best_volume, b->volume);

    free(best_items);
    freeBoundOrders();
    return best_profit;
}
