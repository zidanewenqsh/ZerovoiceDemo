#include "thrd_pool.h"
#include "spinlock.h"
#include <bits/pthreadtypes.h>
#include <pthread.h>
typedef void(*handler_pt)(void *);

typedef struct task_s {
    void *next;
    handler_pt func;
    void *arg;
} task_t;

typedef struct taskqueue_s {
    void *head;
    void **tail;
    int block;
    spinlock_t lock;
    pthread_mutex_t mutex;
    pthread_cond_t cond;
} taskqueue_t;

typedef struct thrdpool_s {
    taskqueue_t *queue;
    pthread_t *threads;
    int thread_count;
    atomic_int quit;
} thrdpool_t;

static taskqueue_t* __taskqueue_init() {
    taskqueue_t *queue = (taskqueue_t*)malloc(sizeof(taskqueue_t));
    if (queue == NULL) {
        return NULL;
    }
    int ret = pthread_mutex_init(&queue->mutex, NULL);
    if (ret == 0) {
        ret = pthread_cond_init(&queue->cond, NULL);
        if (ret == 0) {
            spinlock_init(&queue->lock);
            queue->head = NULL;
            queue->tail = &queue->head;
            queue->block = 1;
            return queue; 
        }
        pthread_cond_destroy(&queue->cond);
    }
    pthread_mutex_destroy(&queue->mutex);
    return NULL;
}
static inline void __addtask(taskqueue_t* queue, void *task) {
    void **link = (void **)task;
    *link = NULL;
    spinlock_lock(&queue->lock);
    *queue->tail = link;
    queue->tail = link;
    spinlock_unlock(&queue->lock);
    pthread_cond_signal(&queue->cond);
}

static inline void *__poptask(taskqueue_t* queue) {
    spinlock_lock(&queue->lock);
    if (queue->head == NULL) {
        spinlock_unlock(&queue->lock);
        return NULL;
    }
    void *task = queue->head;
    queue->head = *(void**)task;
    if (queue->head == NULL) {
        queue->tail = &queue->head;
    }
    spinlock_unlock(&queue->lock);
    return task;
}

static inline void* __gettask(taskqueue_t *queue) {
    void *task;
    while ((task = __poptask(queue)) == NULL) {
        pthread_mutex_lock(&queue->mutex);
        if (queue->block == 0) {
            pthread_mutex_unlock(&queue->mutex);
            return NULL;
        }
        pthread_cond_wait(&queue->cond, &queue->mutex);
        pthread_mutex_unlock(&queue->mutex);
    }
    return task;
}
static inline void __nonblock(taskqueue_t *queue) {
    pthread_mutex_lock(&queue->mutex);
    queue->block = 0;
    pthread_mutex_unlock(&queue->mutex);
    pthread_cond_broadcast(&queue->cond);
}

static void __taskqueue_destroy(taskqueue_t *queue) {
    __nonblock(queue);
    void *task;
    while ((task = __poptask(queue)) != NULL) {
        free(task);
        task = NULL;
    }
    spinlock_destroy(&queue->lock);
    pthread_cond_destroy(&queue->cond);
    pthread_mutex_destroy(&queue->mutex);
    free(queue);
    queue = NULL;
}

static void* __thrdpool_worker(void *arg) {
    thrdpool_t *pool = (thrdpool_t*)arg;
    task_t* task;
    void *ctx;
    while (atomic_load(&pool->quit) == 0) {
        task = (task_t*)__gettask(pool->queue);
        if (!task) break;
        handler_pt func = task->func;
        ctx = task->arg;
        free(task);
        task = NULL;
        func(ctx);
    }
    return NULL;
}

static void __thread_terminate (thrdpool_t *pool) {
    atomic_store(&pool->quit, 1);
    __nonblock(pool->queue);
    for (int i = 0; i < pool->thread_count; i++) {
        pthread_join(pool->threads[i], NULL);
    }
}

static int __thread_create(thrdpool_t *pool) {
    pthread_attr_t attr;
    int ret;
    ret = pthread_attr_init(&attr);
    if (ret == 0) {
        pool->threads = (pthread_t*)malloc(sizeof(pthread_t) * pool->thread_count);
        if (pool->threads) {
            int i = 0;
            for (; i < pool->thread_count; i++) {
                ret = pthread_create(&pool->threads[i], &attr, __thrdpool_worker, pool);
                if (ret != 0 )break;
            }
            pthread_attr_destroy(&attr);
            if (i == pool->thread_count) {
                return 0;
            }
            __thread_terminate(pool);
            free(pool->threads);
            pool->threads = NULL;
            // return -1;
        } else {
            pthread_attr_destroy(&attr);
            // return -1;
        }
    }
    return -1;
}


void thrdpool_terminate(thrdpool_t *pool) {
    atomic_store(&pool->quit, 1);
    __nonblock(pool->queue);
}

thrdpool_t *thrdpool_create(int thrd_count) {
    thrdpool_t *pool = (thrdpool_t*)malloc(sizeof(thrdpool_t));
    if (pool == NULL) {
        return NULL;
    }
    taskqueue_t* queue = __taskqueue_init();
    if (queue) {
        pool->queue = queue;
        pool->thread_count = thrd_count;
        atomic_init(&pool->quit, 0);
        if (__thread_create(pool) == 0) {
            return pool;
        }
        // __thread_terminate(pool);
        __taskqueue_destroy(queue);
    }
    free(pool);
    pool = NULL;
    return NULL;
}

int thrdpool_post(thrdpool_t *pool, handler_pt func, void *args) {
    if (atomic_load(&pool->quit) == 1) {
        return -1; 
    }
    task_t *task = (task_t*)malloc(sizeof(task_t));
    if (task == NULL) {
        return -1;
    }
    task->func = func;
    task->arg = args;
    __addtask(pool->queue, task);
    return 0;
}

void thrdpool_waitdone (thrdpool_t *pool) {
    for (int i = 0; i < pool->thread_count; i++) {
        pthread_join(pool->threads[i], NULL);
    }
    __taskqueue_destroy(pool->queue);
    free(pool->threads);
    pool->threads = NULL;
    free(pool);
    pool = NULL;
}