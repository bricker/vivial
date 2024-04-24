#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <libpq-fe.h>
#include <curl/curl.h>
#include <pthread.h>
#include "notify_handler.h"
#include "../queue/queue.h"

#define N_THREADS 4
#define HUNDRED_MILLIS 100000
#define CHECK_CURLCODE_OK(res) \
  do { \
    if (res != CURLE_OK) { \
      fprintf(stderr, "Error making network request to Eave: %s\n", curl_easy_strerror(res)); \
      return 1; \
    } \
  } while(0)

typedef struct notif_handler_params {
  char* jsonBody;
} notif_handler_params_t;

static void freeHandlerParams(notif_handler_params_t* params) {
  free(params->jsonBody);
  free(params);
}

/**
 * Makes a POST request, sending `jsonBody` as the request body.
 *
 * @return 0 on success, 1 on error
 */
static int postJSONToEave(char* jsonBody) {
  CURLcode res;
  CURL *curl = curl_easy_init();
  if (curl == NULL) {
    fprintf(stderr, "Error initializing cURL networking client\n");
    return 1;
  }

  // TODO: update to real backend URL
  res = curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8080");
  CHECK_CURLCODE_OK(res);

  struct curl_slist* headers = NULL;
  headers = curl_slist_append(headers, "Content-Type: application/json");
  if (headers == NULL) {
    fprintf(stderr, "Error creating cURL networking request\n");
    return 1;
  }
  res = curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
  CHECK_CURLCODE_OK(res);

  // from man page: "This function does not accept input strings longer than CURL_MAX_INPUT_LENGTH (8 MB)"
  // (we should never reach that in practice, because pg_notify payload (where jsonBody originates)
  // can be only 8 KB maximum)
  res = curl_easy_setopt(curl, CURLOPT_COPYPOSTFIELDS, jsonBody);
  CHECK_CURLCODE_OK(res);

  // Perform the POST request
  res = curl_easy_perform(curl);
  CHECK_CURLCODE_OK(res);

  curl_slist_free_all(headers);
  curl_easy_cleanup(curl);
  return 0;
}

/**
 * Function to be executed on a thread for handling a data change notification from
 * postgres.
 * This function will free its params after completing use.
 *
 * @param param queue_t* to monitor for events to handle
 */
void* handleNotifications(void * param) {
  queue_t* q = (queue_t*)param;
  while (1) {
    if (q->len > 0) {
      notif_handler_params_t* notifParams = (notif_handler_params_t*)dequeue(q);
      // make sure q data didnt get consumed by another thread
      if (notifParams != NULL) {
        // TODO: preprocessing to avoid sending PII to eave

        postJSONToEave(notifParams->jsonBody); // TODO: err handle?? retry later?

        freeHandlerParams(notifParams);
      }
    }

    // improve how we do delay??
    usleep(HUNDRED_MILLIS);
  }
  return NULL;
}

/**
 * Endlessly poll the db connection for notifications.
 * Precondition: Expects a LISTEN command to already have been executed on `conn`.
 *
 * @return 1 on error and doesn't return while successful
 */
int pollForNotifications(PGconn* conn) {
  PGnotify *notify;

  // manual init cURL for future network reqs (for thread safety)
  if (curl_global_init(CURL_GLOBAL_ALL)) {
    fprintf(stderr, "Error initializing cURL networking client\n");
    return 1;
  }

  queue_t* notifQueue = NULL;
  if (initQueue(&notifQueue)) {
    fprintf(stderr, "Error initialized notification queue\n");
    return 1;
  }

  // launch consumer threads
  pthread_t threads[N_THREADS];
  for (int i = 0; i < N_THREADS; i++) {
    pthread_create(&threads[i], NULL, handleNotifications, (void*)notifQueue);
  }

  // poll for anything from our pg connection, producing events on queue for threads
  while (1) {
    PQconsumeInput(conn);

    // Check for any pending notifications
    while ((notify = PQnotifies(conn)) != NULL) {
      // printf("Received notification from channel %s: %s\n", notify->relname, notify->extra);
      // construct thread func params
      notif_handler_params_t* params = malloc(sizeof(notif_handler_params_t));
      size_t jsonLen = strlen(notify->extra);
      char* buff = malloc((jsonLen + 1) * sizeof(char));
      if (params == NULL || buff == NULL) {
        // recover from error; drop this event
        // TODO: is there anything we can do to retry later?
        fprintf(stderr, "Error allocating memory for notification data. Recovering.\n");
        PQfreemem(notify);
        continue;
      }
      // copy in notification body so we can free the notify pointer at end of loop
      memcpy(buff, notify->extra, jsonLen);
      buff[jsonLen] = '\0';
      params->jsonBody = buff;

      // push notification onto queue to be handled by consumer threads
      if (enqueue(notifQueue, (void*)params)) {
        // recover from error; drop this event
        // TODO: is there anything we can do to retry later?
        fprintf(stderr, "Failed to enqueue notification data. Recovering.\n");
        PQfreemem(notify);
        continue;
      }

      // cleanup
      PQfreemem(notify);
    }

    // improve how we do delay??
    usleep(HUNDRED_MILLIS);
  }

  // should never get here.. but cleanup code
  // pthread_join
  curl_global_cleanup();
  return 1;
}
