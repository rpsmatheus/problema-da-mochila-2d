#ifndef __STRUCTURES_H__
#define __STRUCTURES_H__

typedef int WeighType;
typedef int ValueType;
typedef int VolumeType; // Novo tipo para volume

typedef struct item {
    ValueType value;
    WeighType weigh;
    VolumeType volume; // <--- Adicionado
} Item;

typedef struct backpack {
    WeighType weigh;     // Capacidade de Peso (W)
    VolumeType volume;   // <--- Adicionado: Capacidade de Volume (V)
    Item *items;
    int items_amount;
} Backpack;

Item *allocItems(int n);
void freeItems(Item **pp_item);

#endif