#ifndef _LISTENER_
#define _LISTENER_
#include <libpq-fe.h>

void startListening(PGconn* conn);

#endif