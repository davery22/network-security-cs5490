#include <stdlib.h>
#include <stdio.h>
#include <string.h>

typedef unsigned long u_int64;
typedef unsigned char u_int8;

// Helper (for debugging, unused in final version)
void print_hex(char *message) {
    printf("  ");
    int i;
    for (i = 8; i--; ) { // print bytes backwards - because little endian
        printf("%02x ", (u_int8)message[i]);
    }
    printf("\n");
}

void rc4init(u_int8 *state, char *key) {
    u_int8 t, k = 0;

    int i, j;
    for (i = 0; i < 256; i++) {
        state[i] = i;
    }

    for (i = 0, j = 0; i < 256; i++, j = (j + 1) % 8) {
        t = state[i];
        state[i] = state[k += key[j] + t];
        state[k] = t;
    }
}

u_int8 rc4step(u_int8 *state, u_int8 *x, u_int8 *y) {
        u_int8 t = state[*y += state[++*x]];
        state[*y] = state[*x];
        state[*x] = t;
        return state[(state[*x] + state[*y]) % 256];
}

void construct_tables(char **forward_subs, char **backward_subs, char *key) {
    // Initialize the RNG
    u_int8 state[256], x = 0, y = 0;
    rc4init(state, key);

    // Actually build the tables
    int i, j, t;
    for (i = 0; i < 8; i++) {
        forward_subs[i] = malloc(sizeof(char) * 256);
        backward_subs[i] = malloc(sizeof(char) * 256);
        int mapped[256] = {0};

        for (j = 0; j < 256; j++) {
            while (mapped[t = rc4step(state, &x, &y)]) {}
            forward_subs[i][j] = t;
            backward_subs[i][t] = j;
            mapped[t]++;
        }
    }
}

void encrypt(char *message, char *password, char **sub_table) {
    int i, j;
    for (i = 0; i < 16; i++) {
        // XOR, Substitute
        for (j = 0; j < 8; j++) {
            message[j] ^= password[j];
            message[j] = sub_table[j][(u_int8)message[j]];
        }

        // Permute (circular shift left)
        *(u_int64*)message = ((*(u_int64*)message) << 1) | ((*(u_int64*)message) >> 63);

        printf("Enc Round %d:\n%s\n", i, message);
    }
}

void decrypt(char *message, char *password, char **sub_table) {
    int i, j;
    for (i = 0; i < 16; i++) {
        // Permute (circular shift right)
        *(u_int64*)message = ((*(u_int64*)message) >> 1) | ((*(u_int64*)message) << 63);

        // Substitute, XOR
        for (j = 0; j < 8; j++) {
            message[j] = sub_table[j][(u_int8)message[j]];
            message[j] ^= password[j];
        }

        printf("Dec Round %d:\n%s\n", i, message);
    }
}

int main(int argv, char **argc) {
    // Input error checking
    if (argv < 2 || strlen(argc[1]) != 8) {
        printf("Usage: %s [8\"message]\n", argc[0]);
        return 1;
    }

    char *message = argc[1];
    char *password = "password";

    // Construct substitution tables for each message character
    char **forward_subs = malloc(sizeof(char*) * 8), **backward_subs = malloc(sizeof(char*) * 8);
    construct_tables(forward_subs, backward_subs, password);
    
    // Copy the message so we can compare to it later
    char *copy = calloc(1, sizeof(char) * 9);
    int i;
    for (i = 0; i < 8; i++ ) {
        copy[i] = message[i];
    }
    printf("%s\n", copy);

    // Encrypt
    encrypt(copy, password, forward_subs);

    // Decrypt
    decrypt(copy, password, backward_subs);

    return !!(strcmp(copy, message)); // 0 status if they are the same; 1 otherwise
}
