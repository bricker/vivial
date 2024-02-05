#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libpq-fe.h>

/*
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

/**
 * Returns a string containing triggers.sql file content.
 * Caller is responsible for freeing the returned string.
 */
char* readSQLFile() {
  FILE* file = fopen("./src/listener/triggers.sql", "r");
  if (file == NULL) {
    perror("Error opening triggers.sql file");
    exit(EXIT_FAILURE);
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
 */
char* appendListenerInvocations(char* currSqlCommand) {
    // append invocation ops to the read sql function context
  char* listenOps[2] = {
    "CALL eave_install_triggers();",
    "LISTEN eave_dbchange_channel;"
  };
  int opsLen = sizeof(listenOps) / sizeof(listenOps[0]);

  for (int i = 0; i < opsLen; i++) {
    char* nextCmd = listenOps[i];

    size_t currLen = strlen(currSqlCommand);
    size_t addLen = strlen(nextCmd);

    // Allocate memory for the concatenated string plus the null terminator
    char* buff = malloc(currLen + addLen + 1);
    if (buff == NULL) {
        perror("Memory allocation error");
        exit(EXIT_FAILURE);
    }

    // slap both those bad boys in there together
    strcpy(buff, currSqlCommand);
    strcat(buff, nextCmd);

    // make buff new curr cmd
    free(currSqlCommand);
    currSqlCommand = buff;
  }
}

/**
 * Starts listening for notifications on the trigger functions defined in the triggers.sql file.
 * **IMPORTANT**
 * LISTEN registers the _current_ session as a listener. Whenever NOTIFY is invoked by SQL/database, only the sessions
 * _currently_ listening on that notification channel are notified.
 *
 * @param conn - a postgres libpq database connection         
 */
void startListening(PGconn* conn) {
  char* currSqlCommand = readSQLFile();
  appendListenerInvocations(currSqlCommand);

  // execute the built sql commands

  printf("%s\n", currSqlCommand);

  free(currSqlCommand);

}