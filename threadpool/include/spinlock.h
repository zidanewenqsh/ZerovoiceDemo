#ifndef SPINLOCK_H
#define SPINLOCK_H
// spinlock declarations
#define atomic_value_type_(p, v) v
#if defined (__cplusplus)
#include <atomic>
#define STD_ std::
#define atomic_value_type_(p, v) decltype((p)->load())(v) 
#else
#include <stdatomic.h>
#define STD_
#define atomic_value_type_(p, v) v
#endif
#include <immintrin.h>
#define atomic_pause_() _mm_pause()

#define ATOM_INT  STD_ atomic_int
#define ATOM_POINTER STD_ atomic_uintptr_t
#define ATOM_SIZET STD_ atomic_size_t
#define ATOM_ULONG STD_ atomic_ulong
#define ATOM_INIT(ref, v) STD_ atomic_init(ref, v)
#define ATOM_LOAD(ptr) STD_ atomic_load(ptr)
#define ATOM_STORE(ptr, v) STD_ atomic_store(ptr, v)

#define atomic_test_and_set_(ptr) STD_ atomic_exchange_explicit(ptr, 1, STD_ memory_order_acquire)
#define atomic_clear_(ptr) STD_ atomic_store_explicit(ptr, 0, STD_ memory_order_release);
#define atomic_load_relaxed_(ptr) STD_ atomic_load_explicit(ptr, STD_ memory_order_relaxed)

typedef struct spinlock_s {
    ATOM_INT lock;
} spinlock_t;

static inline void spinlock_init(spinlock_t *lock) {
    ATOM_INIT(&lock->lock, 0);
}

static inline void 
spinlock_lock(spinlock_t *lock) {
    for (;;) {
        if (!atomic_test_and_set_(&lock->lock)) {
            return;
        }
        while (atomic_load_relaxed_(&lock->lock)) {
            atomic_pause_();
        }
    }
}
static inline void 
spinlock_unlock(spinlock_t *lock) {
    atomic_clear_(&lock->lock);
}

static inline void
spinlock_destroy(spinlock_t *lock) {
	(void) lock;
}

int spinlock_main();

#endif
