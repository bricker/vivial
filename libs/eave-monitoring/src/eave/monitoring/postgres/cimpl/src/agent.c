#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libpq-fe.h>
#include "listener/listener.h"
#include "notify_handler/notify_handler.h"

// this is gross but we need this later for initializing PGconn
#define FIELDS_IN_ARGS_T_PLUS_ONE 8

/*
Long-term improvements:
- resilience to failures (dont let http err, or db issue take down whole agent)
- scalability w/ multiple (or rapidly changing) databases
- handle sigint/sigterm to do db conn cleanup? not sure if this can leave dangling connections open on exit
*/

typedef struct args {
  char* conn_str;
  char* host;
  char* hostaddr;
  char* port;
  char* dbname;
  char* user;
  char* password;
} args_t;

static void cleanExit(PGconn* conn) {
  PQfinish(conn);
  exit(EXIT_FAILURE);
}

int isPrefix(const char *pre, const char *str) {
  return strncmp(pre, str, strlen(pre)) == 0;
}

char* parseValueAfter(char sep, char* s) {
  int len = strlen(s);
  int sepPos = 0;
  while (sepPos < len && s[sepPos] != sep) {
    sepPos++;
  }
  if (sepPos >= len-1) {
    return NULL;
  }

  int valLen = len - sepPos;
  char* buf = malloc(sizeof(char) * (valLen + 1));
  if (buf == NULL) {
    fprintf(stderr, "Error allocating memory while parsing input\n");
    exit(EXIT_FAILURE);
  }
  // copy only mem after sep char
  memcpy(buf, s+sepPos+1, valLen);
  buf[valLen] = '\0';
  return buf;
}

static void printHelp() {
  // https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-PARAMKEYWORDS
  printf("Usage: agent [OPTIONS...]\n\n");
  printf("\t    --help\t\tprint this message\n");
  printf("\t-c, --conn=CONN\t\tconnection string for a database\n");
  printf("\t-h, --host=HOST\t\tname of host to connect to, or UNIX socket path\n");
  printf("\t-H, --hostaddr=HOSTADDR\tIP addr of host to connect to\n");
  printf("\t-p, --port=PORT\t\tport number to connect to at server host, or socket file extension\n");
  printf("\t-d, --dbname=DBNAME\tdatabase name to connect to\n");
  printf("\t-u, --user=USER\t\tpostgresql user name to connect as\n");
  printf("\t-p, --password=PASSWORD\tpassword to be used if server demands password auth\n");
  printf("\nProvide either a connection string, or whatever combination of the other args you require.\n");
}

/**
 * Populate `args` w/ data from `argv`.
 */
static void parseArgs(int argc, char** argv, args_t* args) {
  for (int i = 1; i < argc; i++) {
    char* arg = argv[i];
    if (isPrefix("--help", arg)) {
      printHelp();
      exit(EXIT_SUCCESS);
    } else if (isPrefix("-c", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -c flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->conn_str = argv[++i];
    } else if (isPrefix("--conn=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->conn_str = val;
    } else if (isPrefix("-h", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -h flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->host = argv[++i];
    } else if (isPrefix("--host=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->host = val;
    } else if (isPrefix("-H", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -H flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->hostaddr = argv[++i];
    } else if (isPrefix("--hostaddr=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->hostaddr = val;
    } else if (isPrefix("-p", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -p flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->port = argv[++i];
    } else if (isPrefix("--port=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->port = val;
    } else if (isPrefix("-d", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -d flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->dbname = argv[++i];
    } else if (isPrefix("--dbname=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->dbname = val;
    } else if (isPrefix("-u", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -u flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->user = argv[++i];
    } else if (isPrefix("--user=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->user = val;
    } else if (isPrefix("-p", arg)) {
      if (i+1 >= argc) {
        // no value provided for last flag
        fprintf(stderr, "Error: expected a value for -p flag\n");
        exit(EXIT_FAILURE);
      }
      // consume next arg
      args->password = argv[++i];
    } else if (isPrefix("--password=", arg)) {
      char* val = parseValueAfter('=', arg);
      args->password = val;
    } else {
      fprintf(stderr, "Unrecognized option: %s\n", arg);
      exit(EXIT_FAILURE);
    }
  }
}

static PGconn* buildConnection(args_t args) {
  // fields in args_t struct + 1 (for array NULL term)
  char* kw[FIELDS_IN_ARGS_T_PLUS_ONE];
  char* vals[FIELDS_IN_ARGS_T_PLUS_ONE];
  memset(kw, 0, FIELDS_IN_ARGS_T_PLUS_ONE);
  memset(vals, 0, FIELDS_IN_ARGS_T_PLUS_ONE);

  int i = 0;
  if (args.conn_str) {
    // dbname here is intentional; PQconnectdbParams will expand first
    // dbname entry to a connection string if the expand_dbname parameter is true
    kw[i] = "dbname";
    vals[i] = args.conn_str;
    i++;
  }
  if (args.host) {
    kw[i] = "host";
    vals[i] = args.host;
    i++;
  }
  if (args.hostaddr) {
    kw[i] = "hostaddr";
    vals[i] = args.hostaddr;
    i++;
  }
  if (args.port) {
    kw[i] = "port";
    vals[i] = args.port;
    i++;
  }
  if (args.dbname) {
    kw[i] = "dbname";
    vals[i] = args.dbname;
    i++;
  }
  if (args.user) {
    kw[i] = "user";
    vals[i] = args.user;
    i++;
  }
  if (args.password) {
    kw[i] = "password";
    vals[i] = args.password;
    i++;
  }

  // https://www.postgresql.org/docs/current/libpq-connect.html
  PGconn* conn = PQconnectdbParams(
    (const char *const *)kw,
    (const char *const *)vals,
    args.conn_str != NULL // expand_dbname = True, means interpret dbname kw as a connection string
  );
  return conn;
}

// postgresql://eave_db_user:secruity@localhost:5432/eave
int main(int argc, char** argv) {
  if (argc < 2) {
    // TODO check env vars
    printHelp();
    return EXIT_SUCCESS;
  }

  args_t args;
  // later behavior depends on null values in unset struct fields
  memset(&args, 0, sizeof(args_t));
  parseArgs(argc, argv, &args);

  PGconn* conn = buildConnection(args);
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