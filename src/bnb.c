#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>
#include <math.h>
#include "../headers/bnb.h"

/* =========================================================
   VARIÁVEIS GLOBAIS (para print)
   ========================================================= */
static bool *best_items = NULL;
static int best_weight = 0;
static int best_volume = 0;

/* =========================================================
   PRIORITY QUEUE
   ========================================================= */

int compareNodes(const void *a, const void *b) {
    Node *n1 = *(Node **)a;
    Node *n2 = *(Node **)b;
    if (n1->bound < n2->bound) return 1;
    if (n1->bound > n2->bound) return -1;
    return 0;
}

PriorityQueue *createPriorityQueue() {
    PriorityQueue *pq = malloc(sizeof(PriorityQueue));
    pq->capacity = 1024;
    pq->size = 0;
    pq->nodes = malloc(sizeof(Node *) * pq->capacity);
    return pq;
}

void enqueue(PriorityQueue *pq, Node *node) {
    if (pq->size >= pq->capacity) {
        pq->capacity *= 2;
        pq->nodes = realloc(pq->nodes,
                             pq->capacity * sizeof(Node *));
    }
    pq->nodes[pq->size++] = node;
    qsort(pq->nodes, pq->size, sizeof(Node *), compareNodes);
}

Node *dequeue(PriorityQueue *pq) {
    if (pq->size == 0) return NULL;
    Node *top = pq->nodes[0];
    memmove(&pq->nodes[0], &pq->nodes[1],
            (pq->size - 1) * sizeof(Node *));
    pq->size--;
    return top;
}

bool isEmpty(PriorityQueue *pq) {
    return pq->size == 0;
}

void freeQueue(PriorityQueue *pq) {
    for (int i = 0; i < pq->size; i++) {
        free(pq->nodes[i]->selected_items);
        free(pq->nodes[i]);
    }
    free(pq->nodes);
    free(pq);
}

/* =========================================================
   ORDENAÇÃO POR EFICIÊNCIA (APENAS PESO)
   ========================================================= */

int compararItensEficiencia(const void *a, const void *b) {
    Item *i1 = (Item *)a;
    Item *i2 = (Item *)b;
    double r1 = (double)i1->value / i1->weigh;
    double r2 = (double)i2->value / i2->weigh;
    if (r1 < r2) return 1;
    if (r1 > r2) return -1;
    return 0;
}

/* =========================================================
   NÓS
   ========================================================= */

Node *createNode(int level, WeighType weight, VolumeType volume,
                 ValueType profit, int items_amount) {
    Node *node = malloc(sizeof(Node));
    node->level = level;
    node->weight = weight;
    node->volume = volume;
    node->profit = profit;
    node->bound = 0.0f;
    node->selected_items = calloc(items_amount, sizeof(bool));
    return node;
}

Node *copyNode(Node *src, int items_amount) {
    Node *copy = createNode(src->level, src->weight,
                            src->volume, src->profit,
                            items_amount);
    memcpy(copy->selected_items, src->selected_items,
           items_amount * sizeof(bool));
    return copy;
}

/* =========================================================
   BOUND CORRETO (ADMISSÍVEL)
   ========================================================= */

float calculateBound(Node *node, Backpack *b) {

    if (node->weight > b->weigh)
        return 0;

    float bound = node->profit;
    int totalWeight = node->weight;
    int j = node->level + 1;

    while (j < b->items_amount &&
           totalWeight + b->items[j].weigh <= b->weigh) {

        totalWeight += b->items[j].weigh;
        bound += b->items[j].value;
        j++;
    }

    if (j < b->items_amount) {
        float fraction =
            (float)(b->weigh - totalWeight) / b->items[j].weigh;
        bound += b->items[j].value * fraction;
    }

    return bound;
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

/* =========================================================
   BRANCH AND BOUND
   ========================================================= */

int branchAndBoundApproach(Backpack *b, clock_t start_time) {

    printf("Executando Branch and Bound (Limite 1h)...\n");

    qsort(b->items, b->items_amount, sizeof(Item),
          compararItensEficiencia);

    int best_profit = 0;
    best_items = calloc(b->items_amount, sizeof(bool));
    best_profit = generateInitialSolution(b);

    Node *root = createNode(-1, 0, 0, 0, b->items_amount);
    root->bound = calculateBound(root, b);

    PriorityQueue *pq = createPriorityQueue();
    enqueue(pq, root);

    while (!isEmpty(pq)) {

        double elapsed = (double)(clock() - start_time) / CLOCKS_PER_SEC;
        if (elapsed > 3600.0) {
            printf("\n[TIMEOUT] Branch and Bound atingiu 1h!\n");
            break;
        }

        Node *u = dequeue(pq);

        if (u->bound < best_profit) {
            free(u->selected_items);
            free(u);
            continue;
        }

        int level = u->level + 1;
        if (level >= b->items_amount) {
            free(u->selected_items);
            free(u);
            continue;
        }

        /* INCLUDE */
        Node *incl = copyNode(u, b->items_amount);
        incl->level = level;
        incl->weight += b->items[level].weigh;
        incl->volume += b->items[level].volume;
        incl->profit += b->items[level].value;
        incl->selected_items[level] = true;

        if (incl->weight <= b->weigh && incl->volume <= b->volume) {
            if (incl->profit > best_profit) {
                best_profit = incl->profit;
                best_weight = incl->weight;
                best_volume = incl->volume;
                memcpy(best_items, incl->selected_items,
                       b->items_amount * sizeof(bool));
            }

            incl->bound = calculateBound(incl, b);
            if (incl->bound >= best_profit)
                enqueue(pq, incl);
            else {
                free(incl->selected_items);
                free(incl);
            }
        } else {
            free(incl->selected_items);
            free(incl);
        }

        /* EXCLUDE */
        Node *excl = copyNode(u, b->items_amount);
        excl->level = level;
        excl->bound = calculateBound(excl, b);

        if (excl->bound >= best_profit)
            enqueue(pq, excl);
        else {
            free(excl->selected_items);
            free(excl);
        }

        free(u->selected_items);
        free(u);
    }

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
    freeQueue(pq);
    return best_profit;
}
