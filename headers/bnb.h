#ifndef MOCHILABRANCH_H
#define MOCHILABRANCH_H

#include "../headers/structures.h"
#include <stdbool.h>
#include <time.h>


typedef struct Node {
    int level;
    WeighType weight;
    VolumeType volume; 
    ValueType profit;
    float bound;
    unsigned long long *selected_items;
} Node;


int branchAndBoundApproach(Backpack* b, clock_t start_time);

#endif