#ifndef THRD_POOL_H
#define THRD_POOL_H
// Module declarations
#include <stdio.h>
#include <pthread.h>
#include "spinlock.h"
typedef struct thrdpool_s thrdpool_t;
typedef void (*handler_pt)(void *);

#ifdef __cplusplus
extern "C"
{
#endif

// 对称处理
thrdpool_t *thrdpool_create(int thrd_count);

void thrdpool_terminate(thrdpool_t * pool);

int thrdpool_post(thrdpool_t *pool, handler_pt func, void *arg);

void thrdpool_waitdone(thrdpool_t *pool);

#ifdef __cplusplus
}
#endif
#endif