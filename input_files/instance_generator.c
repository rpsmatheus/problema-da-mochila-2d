#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>

#define INSTANCES_PER_COMBINATION 10

void showUsage(char *program_name) {
    printf("Uso: %s <n_itens> <cap_peso_W> <cap_volume_V> [seed]\n", program_name);
}

bool enoughArgs(int argc) { return argc == 4 || argc == 5; }

void fillFile(FILE *file, int W, int V, int n) {
    int max_item_weight = W;
    int max_item_vol    = V;
    int max_item_value  = 1000;

    fprintf(file, "%d\t%d", W, V);

    for (int i = 0; i < n; i++) {
        int peso  = (rand() % max_item_weight) + 1;
        int vol   = (rand() % max_item_vol)    + 1;
        int valor = (rand() % max_item_value)  + 1;

        fprintf(file, "\n%d\t%d\t%d", peso, vol, valor);
    }

    fprintf(file, "\n");
}

int main(int argc, char *argv[]) {
    if (!enoughArgs(argc)) {
        showUsage(argv[0]);
        exit(1);
    }

    int n = atoi(argv[1]);
    int W = atoi(argv[2]);
    int V = atoi(argv[3]);

    if (n <= 0 || W <= 0 || V <= 0) {
        fprintf(stderr, "Erro: todos os parametros numericos devem ser positivos.\n");
        exit(1);
    }

    unsigned int seed;
    if (argc == 5) {
        seed = (unsigned int) atol(argv[4]);
    } else {
        seed = (unsigned int) time(NULL) ^ (unsigned int) clock() ^ (unsigned int) getpid();
    }

    printf("Seed: %u\n", seed);

    for (int instance_id = 1; instance_id <= INSTANCES_PER_COMBINATION; instance_id++) {
        /* Cada instancia tem sua propria seed derivada da seed base,
           garantindo que sejam diferentes entre si mas ainda reproduziveis. */
        srand(seed + (unsigned int) instance_id);

        char file_name[128];
        sprintf(file_name, "instancia_n%d_W%d_V%d_i%d.txt", n, W, V, instance_id);

        FILE *output = fopen(file_name, "w");
        if (!output) {
            perror("Falha ao criar instancia");
            exit(1);
        }

        fillFile(output, W, V, n);
        fclose(output);

        printf("Instancia gerada com sucesso: %s\n", file_name);
    }

    return 0;
}