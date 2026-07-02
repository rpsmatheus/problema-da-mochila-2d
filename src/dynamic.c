#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <string.h>
#include <stdbool.h>
#include "../headers/dynamic.h"

typedef struct memo {
    int items_amount;
    int capacity_weight;
    int capacity_volume;
    int ***table; 
} Memo;

static Memo m;
static bool timeout_dynamic = false;

// Alocada e inicializada com 0 
int ***allocMemoTable(unsigned int cap_weight, unsigned int cap_volume, unsigned int items_amount)
{
    m.table = (int***) malloc((items_amount + 1) * sizeof(int**));
    if(m.table == NULL) return NULL;

    for(unsigned int i = 0 ; i <= items_amount ; i++)
    {
        m.table[i] = (int**) malloc((cap_weight + 1) * sizeof(int*));
        if(m.table[i] == NULL) return NULL;

        for(unsigned int j = 0 ; j <= cap_weight ; j++)
        {
            m.table[i][j] = (int*) malloc((cap_volume + 1) * sizeof(int));
            if(m.table[i][j] == NULL) return NULL;

            
            for(unsigned int k = 0 ; k <= cap_volume ; k++)
                m.table[i][j][k] = 0;
        }
    }

    m.capacity_weight = cap_weight;
    m.capacity_volume = cap_volume;
    m.items_amount = items_amount;
    return m.table;
}

void freeMemoTable()
{
    for(int i = 0 ; i <= m.items_amount ; i++) {
        for(int j = 0 ; j <= m.capacity_weight ; j++) {
            free(m.table[i][j]);
        }
        free(m.table[i]);
    }
    free(m.table);
}

int maxValue(int a, int b) { return a > b ? a : b; }

int dynamic(Item *items, int n, int W, int V, clock_t start_time)
{
    int check_counter = 0;

    // Se não há itens ou capacidades, lucro é 0 
    if(n == 0 || W <= 0 || V <= 0) return 0;

    // Construção Bottom-Up
    for (int i = 1; i <= n; i++) {
        for (int w = 1; w <= W; w++) {
            for (int v = 1; v <= V; v++) {
                
                // Verificação de timeout 
                if (check_counter++ % 10000 == 0) {
                    double elapsed = (double)(clock() - start_time) / CLOCKS_PER_SEC;
                    if (elapsed > 7200.0) {
                        timeout_dynamic = true;
                        return 0; // Aborta 
                    }
                }

                if (items[i - 1].weigh > w || items[i - 1].volume > v) {
                    m.table[i][w][v] = m.table[i - 1][w][v];
                } 
                else {
                    int val_without_item = m.table[i - 1][w][v];
                    int val_with_item = m.table[i - 1][w - items[i - 1].weigh][v - items[i - 1].volume] + items[i - 1].value;
                    
                    m.table[i][w][v] = maxValue(val_without_item, val_with_item);
                }
            }
        }
    }

    return m.table[n][W][V];
}

void showProfitAndItems(Item *items, int profit)
{
    if (timeout_dynamic) {
        printf("\n[TIMEOUT] Programacao Dinamica interrompida apos 2h!\n");
    }

    printf("Lucro máximo: R$ %d\n", profit);
    printf("Itens colocados na mochila:\n");

    int i = m.items_amount;
    int j = m.capacity_weight;
    int k = m.capacity_volume;

    int peso_total = 0;
    int volume_total = 0;

    while (i > 0 && j > 0 && k > 0) {

        // Verifica se o item i-1 foi incluído na solução ótima
        if (items[i - 1].weigh <= j &&
            items[i - 1].volume <= k &&
            m.table[i][j][k] == m.table[i - 1][j - items[i - 1].weigh][k - items[i - 1].volume] + items[i - 1].value)
        {

            printf("\t(Item: %d, Valor: %d, Peso: %d, Volume: %d)\n",
                   i,
                   items[i - 1].value,
                   items[i - 1].weigh,
                   items[i - 1].volume);

            peso_total += items[i - 1].weigh;
            volume_total += items[i - 1].volume;

            j -= items[i - 1].weigh;
            k -= items[i - 1].volume;
        }

        i--;
    }

    printf("Peso total: %d / %d\n", peso_total, m.capacity_weight);
    printf("Volume total: %d / %d\n", volume_total, m.capacity_volume);
}

int dynamicApproch(Backpack *b, clock_t start_time)
{
    int profit;
    timeout_dynamic = false;

    if(allocMemoTable(b->weigh, b->volume, b->items_amount) == NULL) {
        printf("Erro: Falha de memoria ao alocar tabela DP (Cubo muito grande).\n");
        return -1;
    }

    profit = dynamic(b->items, b->items_amount, b->weigh, b->volume, start_time);
    
    showProfitAndItems(b->items, profit);

    freeMemoTable();
    return profit;
}