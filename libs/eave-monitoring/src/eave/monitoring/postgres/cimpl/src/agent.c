#include <stdio.h>
#include <stdlib.h>
#include <libpq-fe.h>
#include "./listener/listener.h"

/*
Long-term improvements:
- resilience to failures (dont let http err, or db issue take down whole agent)
- scalability w/ multiple (or rapidly changing) databases
*/

/*
TODO:
- accept db connection info (config file, or argv)
- create db connection

- load triggers.sql file
- call SQL to
  - execute trigger function
  - listen on channel

- poll connection for notifications on channel
- find good http library
- on each notification
  - create non-blocking thread/process?
  - make web request sending atom payload to eave backend
  - consider batching atoms to reduce req overhead?
*/

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
    exit(EXIT_FAILURE);
  }

  printf("Eave PostgreSQL agent started (Ctrl-C to stop)\n");

  startListening(conn);

  printf("Done (delete me!)");
  return EXIT_SUCCESS;
}