#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include "listener/listener.h"
#include "notify_handler/notify_handler.h"

/*
Long-term improvements:
- resilience to failures (dont let http err, or db issue take down whole agent)
- scalability w/ multiple (or rapidly changing) databases
- handle sigint/sigterm to do db conn cleanup? not sure if this can leave dangling connections open on exit
*/

static void cleanExit(PGconn* conn) {
  PQfinish(conn);
  exit(EXIT_FAILURE);
}

// TODO: accept argv cli params
int main(int argc, char** argv) {
  // https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
  const char* const* kw = (const char *const []){"dbname", NULL};
  const char* const* vals = (const char *const []){"postgresql://eave_db_user:secruity@localhost:5432/eave", NULL};
  PGconn* conn = PQconnectdbParams(
    kw,
    vals,
    1 // expand_dbname = True, meaning interpret dbname kw as a connection string
  );
  if (PQstatus(conn) != CONNECTION_OK) {
    fprintf(stderr, "Error: Unable to connect to postgres database using provided connection info!\n");
    cleanExit(conn);
  }

  printf("Eave PostgreSQL agent started (Ctrl-C to stop)\n");

  // it's vital these both use the same PGconn instance
  if (startListening(conn)) cleanExit(conn);
  if (pollForNotifications(conn)) cleanExit(conn);

  // should never reach here
  PQfinish(conn);
  return EXIT_SUCCESS;
}