If you change anything in `docker-entrypoint-initdb.d`, you should:

1. Stop the `docker compose` process (eg `docker compose down`).
1. Optionally, run `sudo rm -rf .pgdata`. This is necessary because if there is already a database, the init scripts are not run when the `postgres` container boots up. You can skip this if you don't want to lose all of your postgres data, but you'll need to manually run whatever commands you changed/added in the init scripts.
1. Run `bin/start-dev --build` to rebuild the image before starting.
