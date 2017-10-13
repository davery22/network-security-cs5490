#include <stdio.h>
#include <string.h>

typedef unsigned char uns8;
typedef unsigned short uns16;

static uns8 state[256], x, y; /* 258 octets of state information */
void rc4init(uns8 *key, uns16 length) { /* initialize for encryption / decryption */
    int i;
    uns8 t, j, k = 0;
    for (i = 256; i--; ) {
        state[i] = i;
    }

    for (i = 0, j = 0; i < 256; i++, j = (j + 1) % length) {
        t = state[i];
        state[i] = state[k += key[j] + t];
        state[k] = t;
    }
    
    x = 0;
    y = 0;
}

uns8 rc4step() { /* return next pseudo-random octet */
    uns8 t = state[y += state[++x]];
    state[y] = state[x];
    state[x] = t;
    return state[(state[x] + state[y]) % 256]; // added a modulo to keep index in bounds
}

int main() {
    uns8 *key = "mnbvc";
    rc4init(key, strlen(key));

    int i;
    for (i = 0; i < 512; i++) { // ignore first 512 octets
        rc4step();
    }

    uns8 *msg = "This class is not hard at all.";

    for (i = 0; *(msg + i); i++) {
        printf("%02x ", msg[i] ^ rc4step());
    }
    printf("\n");

    return 0;
}
