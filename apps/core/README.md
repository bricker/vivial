## Database

You can either connect to Cloud SQL using Cloud SQL proxy, or run a Postgres server locally.

### Local Postgres server

This is recommended for development.

1. Install postgres for your operating system
1. Start the postgres service
1. Do any OS specific setup required to init postgres (e.g. login to postgres user and initdb)
1. Create a database user
1. Create a database called `eave` (make sure your db user has access)
1. Update your `.env` file to use your local PG credentials.
  It may look similar to this:

```
EAVE_DB_HOST=localhost
EAVE_DB_NAME=eave
EAVE_DB_DRIVER=postgresql+asyncpg
EAVE_DB_PORT=5432
EAVE_DB_USER=your_user
EAVE_DB_PASS=your_password
EAVE_DB_CONNECTION_STRING=postgresql+asyncpg://your_user:your_password@localhost:5432/eave
```

7. From the `apps/core/` directory (with venv active) run `PYTHONPATH=. python eave_alembic/init_database.py`

### Cloud SQL Proxy

Download the cloud sql proxy [from Google Cloud](https://cloud.google.com/sql/docs/postgres/sql-proxy#install).

Then run the proxy with a command like this:

```bash
./cloud_sql_proxy -instances=eave-production:us-central1:eave-pg-core=tcp:5431
```
