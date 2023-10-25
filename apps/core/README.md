## Database

You can either connect to Cloud SQL using Cloud SQL proxy, or run a Postgres server locally.

### Cloud SQL Proxy

This is recommended for development. The setup script should have installed the cloud sql proxy for you.

1. In the [google cloud console](https://console.cloud.google.com/sql/instances/eave-pg-core-dev/users?project=eavefyi-dev), in the `eavefyi-dev` project, add your google cloud IAM user to `eave-pg-core-dev` Cloud SQL instance.

2. In your `.env` file, add:

```
EAVE_DB_USER="your IAM email"
EAVE_DB_NAME="eave-dev-your_name"
EAVE_DB_HOST="/run/user/1000/.cloudsqlproxy/eavefyi-dev:us-central1:eave-pg-core-dev"
```

Note that EAVE_DB_PASS is unnecessary when using Cloud SQL proxy, so deliberately omitted here.

3. From the `apps/core/` directory, run `bin/setup-db`.

4. From $EAVE_HOME, run `bin/cloud-sql-proxy`

### Local Postgres server

An alternative to running Cloud SQL Proxy, if you prefer.

1. Install postgres for your operating system
1. Start the postgres service
1. Do any OS specific setup required to init postgres (e.g. login to postgres user and initdb)
1. Create a database user
1. Create a database called `eave` (make sure your db user has access)
1. Update your `.env` file to use your local PG credentials.
  It may look similar to this:

```sh
EAVE_DB_HOST=localhost
EAVE_DB_NAME=eave
EAVE_DB_PORT=5432
EAVE_DB_USER=your_user
EAVE_DB_PASS=your_password
```
