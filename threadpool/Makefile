CC=gcc
CFLAGS=-g -Wall -Wl,-rpath,. -Iinclude
LDFLAGS=-Llib -lpthread
SRC_DIR=src
OBJ_DIR=obj
BIN_DIR=bin

SOURCES=$(wildcard $(SRC_DIR)/*.c)
OBJECTS=$(SOURCES:$(SRC_DIR)/%.c=$(OBJ_DIR)/%.o)
TARGET=$(BIN_DIR)/threadpool

all: $(TARGET)

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) $^ -o $@

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ_DIR)/*.o $(TARGET)

.PHONY: all clean
