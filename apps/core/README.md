## Database

You can either connect to Cloud SQL using Cloud SQL proxy, or run a Postgres server locally.

### Local Postgres server

This is recommended for development. WARNING: I have not tested this flow, if there are issues please fix them.

1. Install postgres for your operating system
1. Create a database called `eave`
1. Update your `.env` file to use your local PG credentials
1. Run `python alembic/init_database.py`

### Cloud SQL Proxy

https://cloud.google.com/sql/docs/postgres/sql-proxy#install

Then run the proxy with a command like this:

```bash
./cloud_sql_proxy -instances=eave-production:us-central1:eave-pg-core=tcp:5431
```

