#include "spinlock.h"
// spinlock functions
#include <stdio.h>
#include <pthread.h>
#include "spinlock.h"

#define NUM_THREADS 10

spinlock_t lock;
int counter = 0;

void *test_lock(void *arg) {
    int i;
    for (i = 0; i < 100000; i++) {
        spinlock_lock(&lock);
        counter++;
        spinlock_unlock(&lock);
    }
    return NULL;
}

int spinlock_main() {
    pthread_t threads[NUM_THREADS];
    int i;

    spinlock_init(&lock);

    for (i = 0; i < NUM_THREADS; i++) {
        pthread_create(&threads[i], NULL, test_lock, NULL);
    }

    for (i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }

    printf("Final counter value: %d\n", counter);

    spinlock_destroy(&lock);

    return 0;
}

