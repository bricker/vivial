#ifndef _NOTIFY_HANDLER_
#define _NOTIFY_HANDLER_
#include <libpq-fe.h>

/**
 * Endlessly poll the db connection for notifications.
 * Precondition: Expects a LISTEN command to already have been executed on `conn`.
 */
void pollForNotifications(PGconn* conn);

#endif