CC = gcc
# Flag -O3 para otimização e -I para os headers
CFLAGS = -Wall -Wextra -O3 -I$(INC_DIR)

BUILD_DIR = ./build
OUT_DIR = ./app
SRC_DIR = ./src
INC_DIR = ./headers
INPUT_FILES_DIR = ./input_files

MAIN_FILE       := main.c
SRC_C_FILES     := $(MAIN_FILE) $(wildcard $(SRC_DIR)/*.c)
INST_GEN_C_FILE := $(INPUT_FILES_DIR)/instance_generator.c

O_FILES         := $(patsubst %.c, $(BUILD_DIR)/%.o, $(notdir $(SRC_C_FILES)))
H_FILES         := $(wildcard $(INC_DIR)/*.h)
INST_GEN_O_FILE := $(BUILD_DIR)/instance_generator.o

BIN_FILE      := $(OUT_DIR)/exe
BIN_INST_FILE := $(INPUT_FILES_DIR)/generator

# Alteração aqui: Adicionado -lm para linkar a biblioteca math.h
$(BIN_FILE): $(O_FILES)
	@mkdir -p $(OUT_DIR)
	$(CC) $(O_FILES) -o $@ -lm

# Regra para compilar o objeto do main que está na raiz
$(BUILD_DIR)/main.o: main.c $(H_FILES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

# Regra para compilar os objetos que estão em src/
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c $(H_FILES)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: gen clean

# Atalho para compilar o gerador de instâncias
gen: $(BIN_INST_FILE)

$(BIN_INST_FILE): $(INST_GEN_O_FILE)
	$(CC) $(INST_GEN_O_FILE) -o $@

$(INST_GEN_O_FILE): $(INST_GEN_C_FILE)
	@mkdir -p $(BUILD_DIR)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(BUILD_DIR) $(OUT_DIR) $(BIN_INST_FILE)