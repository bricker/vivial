#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <libpq-fe.h>
#include <curl/curl.h>

// - poll connection for notifications on channel
// - find good http library
// - on each notification
//   - create non-blocking thread/process?
//   - make web request sending atom payload to eave backend
//   - consider batching atoms to reduce req overhead?

/**
 * Makes a POST request, sending `jsonBody` as the request body.
 *
 * @return 0 on success, 1 on error
 */
static int postJSONToEave(char* jsonBody) {
  CURL *curl = curl_easy_init();;
  if (curl == NULL) {
    fprintf(stderr, "Error initializing cURL networking client\n");
    return 1;
  }
  // TODO: update to real backend URL
  curl_easy_setopt(curl, CURLOPT_URL, "http://localhost:8080");
  // from man page: "This function does not accept input strings longer than CURL_MAX_INPUT_LENGTH (8 MB)"
  // (we should never reach that in practice, because pg_notify payload (where jsonBody originates)
  // can be only 8 KB maximum)
  curl_easy_setopt(curl, CURLOPT_POSTFIELDS, jsonBody);

  // Perform the POST request
  CURLcode res = curl_easy_perform(curl);
  if (res != CURLE_OK) {
    fprintf(stderr, "Error making network request to Eave: %s\n", curl_easy_strerror(res));
    return 1;
  }

  curl_easy_cleanup(curl);
  return 0;
}

/**
 * Endlessly poll the db connection for notifications.
 * Precondition: Expects a LISTEN command to already have been executed on `conn`.
 *
 * @return 1 on error and doesn't return while successful
 */
int pollForNotifications(PGconn* conn) {
  const int hundredMillis = 100000;
  PGnotify *notify;

  // manual init cURL for future network reqs (for thread safety)
  if (curl_global_init(CURL_GLOBAL_ALL)) {
    fprintf(stderr, "Error initializing cURL networking client\n");
    return 1;
  }

  while (1) {
    // Check for incoming data from the connection
    PQconsumeInput(conn);

    // Check for any pending notifications
    while ((notify = PQnotifies(conn)) != NULL) {
      // TODO: everything past this point should be async! (thread or process)
      printf("Received notification from channel %s: %s\n", notify->relname, notify->extra);

      // TODO: preprocessing to avoid sending PII to eave

      postJSONToEave(notify->extra);

      PQfreemem(notify);
    }

    // improve how we do delay??
    usleep(hundredMillis);
  }

  // should never get here.. but cleanup code
  curl_global_cleanup();
  return 1;
}
