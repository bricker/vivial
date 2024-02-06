#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <libpq-fe.h>

// - poll connection for notifications on channel
// - find good http library
// - on each notification
//   - create non-blocking thread/process?
//   - make web request sending atom payload to eave backend
//   - consider batching atoms to reduce req overhead?

/**
 * Endlessly poll the db connection for notifications.
 * Precondition: Expects a LISTEN command to already have been executed on `conn`.
 */
void pollForNotifications(PGconn* conn) {
  const int hundredMillis = 100000;
  PGnotify *notify;

  while (1) {
    // Check for incoming data from the connection
    PQconsumeInput(conn);

    // Check for any pending notifications
    while ((notify = PQnotifies(conn)) != NULL) {
      printf("Received notification from channel %s: %s\n", notify->relname, notify->extra);
      PQfreemem(notify);
    }

    // improve how we do delay??
    usleep(hundredMillis);
  }
}
