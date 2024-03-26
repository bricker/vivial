### Development

1. Create a `.env` file.
1. Get `MB_PREMIUM_EMBEDDING_TOKEN` from Google Secret Manager.
1. Add `MB_PREMIUM_EMBEDDING_TOKEN="{the secret value}"` to the `.env` file.
1. Run `bin/start-dev` to start a Postgres instance and a Metabase app with default configuration. The Metabase app will be accessible through the HTTP proxy at `metabase.eave.run:8080`.

You can optionally add other [Metabase environment variables](https://www.metabase.com/docs/latest/configuring-metabase/environment-variables) or [`Postgres` Docker container environment variables](https://hub.docker.com/_/postgres) to `.env` to boot up with specific configuration.

Note that if you change anything in `postgres/docker-entrypoint-initdb.d`, you should:

1. Stop the `docker compose` process (eg `docker compose down`).
1. Optionally, run `sudo rm -rf .pgdata`. This is necessary because if there is already a database, the init scripts are not run when the `postgres` container boots up. You can skip this if you don't want to lose all of your postgres data, but you'll need to manually run whatever commands you changed/added in the init scripts.
1. Run `bin/start-dev --build` to rebuild the image before starting.
