#ifndef MOCHILABRANCH_H
#define MOCHILABRANCH_H

#include "../headers/structures.h"
#include <stdbool.h>

// Aumentamos o tamanho da fila pois o volume gera mais ramificações
#define MAX_QUEUE_SIZE 2000000

typedef struct Node {
    int level;
    WeighType weight;
    VolumeType volume; // Adicionado Volume
    ValueType profit;
    float bound;
    bool *selected_items;
} Node;

typedef struct {
    Node **nodes;
    int size;
    int capacity;
} PriorityQueue;


// Assinaturas das funções
PriorityQueue *createPriorityQueue();
void enqueue(PriorityQueue *pq, Node *node);
Node* dequeue(PriorityQueue *pq);
bool isEmpty(PriorityQueue *pq);
void freeQueue(PriorityQueue *pq);
// De: int branchAndBoundApproach(Backpack*);
// Para:
int branchAndBoundApproach(Backpack* b, clock_t start_time);

#endif