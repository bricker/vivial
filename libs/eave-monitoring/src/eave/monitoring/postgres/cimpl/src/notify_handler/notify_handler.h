#ifndef _NOTIFY_HANDLER_
#define _NOTIFY_HANDLER_
#include <libpq-fe.h>

/**
 * Endlessly poll the db connection for notifications.
 * Precondition: Expects a LISTEN command to already have been executed on `conn`.
 *
 * @return 1 on error and doesn't return while successful
 */
int pollForNotifications(PGconn* conn);

#endif