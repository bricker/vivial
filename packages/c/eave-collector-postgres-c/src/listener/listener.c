#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libpq-fe.h>
#include "listener.h"

/**
 * Returns a string containing triggers.sql file content.
 * Caller is responsible for freeing the returned string.
 * 
 * @return file content string on success, NULL on error
 */
static char* readSQLFile() {
  FILE* file = fopen("./src/listener/triggers.sql", "r");
  if (file == NULL) {
    perror("Error opening triggers.sql file");
    exit(EXIT_FAILURE); // TODO: probs dont exit from here?
  }

  fseek(file, 0, SEEK_END); // Move file pointer to the end to determine file size
  long fileSize = ftell(file);
  fseek(file, 0, SEEK_SET); // Reset file pointer to the beginning

  if (fileSize == -1) {
    perror("Error getting file size");
    fclose(file);
    return NULL;
  }

  char* buffer = malloc(fileSize + 1); // Allocate memory for the entire file plus null terminator

  if (buffer == NULL) {
    perror("Memory allocation error");
    fclose(file);
    return NULL;
  }

  size_t bytesRead = fread(buffer, 1, fileSize, file); // Read file into buffer

  if (bytesRead != (size_t)fileSize) {
    perror("Error reading file");
    free(buffer);
    fclose(file);
    return NULL;
  }

  buffer[fileSize] = '\0'; // Null-terminate the string

  fclose(file);
  return buffer;
}

/**
 * Modifies `currSqlCommand` in place, appending any extra SQL commands
 * required to start listening for database changes.
 *
 * @param currSqlCommand - address of a string to append to (&char*)
 * @return 0 on success, 1 on error
 */
static int appendListenerInvocations(char** currSqlCommand) {
    // append invocation ops to the read sql function context
  char* listenOps[2] = {
    "CALL eave_install_triggers();",
    "LISTEN eave_dbchange_channel;"
  };
  int opsLen = sizeof(listenOps) / sizeof(listenOps[0]);

  for (int i = 0; i < opsLen; i++) {
    char* nextCmd = listenOps[i];

    size_t currLen = strlen(*currSqlCommand);
    size_t addLen = strlen(nextCmd);

    // Allocate memory for the concatenated string plus the null terminator
    char* buff = malloc(currLen + addLen + 1);
    if (buff == NULL) {
      perror("Memory allocation error");
      return 1;
    }

    // slap both those bad boys in there together
    strcpy(buff, *currSqlCommand);
    strcat(buff, nextCmd);

    // make buff new curr cmd
    free(*currSqlCommand);
    *currSqlCommand = buff;
  }
  return 0;
}

/**
 * Starts listening for notifications on the trigger functions defined in the triggers.sql file.
 *
 * Precondition: user/role used to create `conn` must have the TRIGGER privilege on all tables (to create
 * or replace trigger functions on a table), and must also have EXECUTE privilege on the trigger function.
 * https://www.postgresql.org/docs/current/sql-createtrigger.html
 *
 * **IMPORTANT**
 * LISTEN registers the _current_ session as a listener. Whenever NOTIFY is invoked by SQL/database, only the sessions
 * _currently_ listening on that notification channel are notified.
 *
 * @param conn - a postgres libpq database connection
 * @return 0 on success, 1 on error
 */
int startListening(PGconn* conn) {
  char* currSqlCommand = readSQLFile();
  if (currSqlCommand == NULL) {
    return 1;
  }
  if (appendListenerInvocations(&currSqlCommand)) return 1;
  // printf("%s\n", currSqlCommand);

  // execute the built sql commands
  PGresult* result = PQexec(conn, currSqlCommand);
  ExecStatusType resultStatus = PQresultStatus(result);
  if (resultStatus != PGRES_COMMAND_OK) {
    char* statusStr = PQresStatus(resultStatus);
    fprintf(stderr, "Error executing LISTEN command. Got unexpected result status %s: %s\n", statusStr, PQerrorMessage(conn));
    return 1;
  }

  free(currSqlCommand);
  PQclear(result);
  return 0;
}