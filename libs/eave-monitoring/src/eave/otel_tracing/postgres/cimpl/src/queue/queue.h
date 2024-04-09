#ifndef _QUEUE_
#define _QUEUE_
#include <pthread.h>

typedef struct qnode {
  struct qnode* next;
  void* data;
} qnode_t;

typedef struct queue {
  qnode_t* first;
  qnode_t* last;
  unsigned int len;
  pthread_mutex_t mutex;
} queue_t;

/**
 * A convenience initializer for a queue_t.
 * Example:
 * ```
 * queue_t* q = NULL;
 * initQueue(&q);
 * // good to go!
 * ```
 *
 * @return 0 on success, non-zero on failure
 */
int initQueue(queue_t** q);

/**
 * Adds the provided `data` to a node on the back of `q`.
 * Memory of `data` is assumed to be dynamically allocated and will
 * become managed by `q`.
 *
 * @return 0 on success 1 on error
 */
int enqueue(queue_t* q, void* data);

/**
 * Pop a qnode_t off the front of the `q`.
 * Receiver becomes responsible for management of the returned memory.
 *
 * @return the first qnode_t, or NULL if the queue_t is empty.
 */
void* dequeue(queue_t* q);

void freeQueue(queue_t* q);

#endif