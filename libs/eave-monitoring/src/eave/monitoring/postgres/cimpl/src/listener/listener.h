#ifndef _LISTENER_
#define _LISTENER_
#include <libpq-fe.h>

/**
 * Starts listening for notifications on the trigger functions defined in the triggers.sql file.
 * **IMPORTANT**
 * LISTEN registers the _current_ session as a listener. Whenever NOTIFY is invoked by SQL/database, only the sessions
 * _currently_ listening on that notification channel are notified.
 *
 * @param conn - a postgres libpq database connection
 * @return 0 on success, 1 on error
 */
int startListening(PGconn* conn);

#endif