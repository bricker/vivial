#ifndef _QUEUE_
#define _QUEUE_
#include <pthread.h>

typedef struct qnode {
  struct qnode* next;
  void* data;
  size_t dataSize;
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
 * queue_t* q;
 * initQueue(&q);
 * // good to go!
 * ```
 */
void initQueue(queue_t** q);

/**
 * Adds the provided `node` to `q`.
 * Memory stored in `node->data` is assumed to be dynamic and will
 * become managed by `q`.
 */
void enqueue(queue_t* q, qnode_t* node);

/**
 * Pop a qnode_t off the front of the `q`.
 * Receiver becomes responsible for management of the returned memory.
 *
 * @return the first qnode_t, or NULL if the queue_t is empty.
 */
void* dequeue(queue_t* q);

void freeQueue(queue_t* q);

#endif