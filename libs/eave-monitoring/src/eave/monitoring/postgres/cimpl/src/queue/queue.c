#include <stdlib.h>
#include <pthread.h>

/**
 * A convenience initializer for a queue_t.
 * Example:
 * ```
 * queue_t* q = NULL;
 * initQueue(&q);
 * // good to go!
 * ```
 */
void initQueue(queue_t** q) {
  if (*q == NULL) {
    *q = malloc(sizeof(queue_t));
  }
  (*q)->first = NULL;
  (*q)->last = NULL;
  pthread_mutex_init(&(*q)->mutex, NULL);
}

/**
 * Adds the provided `node` to `q`.
 * Memory stored in `node->data` is assumed to be dynamic and will
 * become managed by `q`.
 */
void enqueue(queue_t* q, qnode_t* node) {
  pthread_mutex_lock(&(q->mutex));
  q->len++;

  if (q->first == NULL) {
    q->first = node;
    q->last = node;
    pthread_mutex_unlock(&(q->mutex));
    return;
  }

  q->last->next = node;
  q->last = node;
  pthread_mutex_unlock(&(q->mutex));
}

/**
 * Pop a `qnode_t.data` off the front of the `q`, if possible.
 * Receiver becomes responsible for management of the returned memory.
 *
 * @return the first qnode_t's data, or NULL if the queue_t is empty.
 */
void* dequeue(queue_t* q) {
  if (q->first == NULL) {
    return NULL;
  }
  pthread_mutex_lock(&(q->mutex));
  q->len--;

  void* data = q->first->data;
  if (q->first == q->last) {
    free(q->first);
    q->first = NULL;
    q->last = NULL;
  } else {
    qnode_t* temp = q->first;
    q->first = temp->next;
    free(temp);
  }
  pthread_mutex_unlock(&(q->mutex));
  return data;
}

void freeQueue(queue_t* q) {
  pthread_mutex_lock(&(q->mutex));
  qnode_t* curr = q->first;

  while (curr != NULL) {
    qnode_t* temp = curr;
    curr = curr->next;
    free(temp->data);
    free(temp);
  }

  pthread_mutex_unlock(&(q->mutex));
  free(q);
}