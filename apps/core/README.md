## Database

It is recommended to run a local Postgres server for development.

### Postgres installation and setup

This is very OS-specific and there are many options. Find your OS [here](https://www.postgresql.org/download/) and follow the instructions.

The goal is to have a Postgres server running locally. There are many tutorials on the internet that you can follow to accomplish this.

To give an example, on Ubuntu these are some useful commands:

```sh
sudo service postgres start
sudo -u postgres createuser --interactive
```

### Application configuration

Update your `.env` file to add the Postgres server information and your credentials. It may look similar to this:

```sh
EAVE_DB_HOST="/var/run/postgresql"
EAVE_DB_PORT="5433"
EAVE_DB_USER="bryan"
EAVE_DB_PASS="your_password"
EAVE_DB_NAME="eave-development"
```

### Eave Database initialization

Run `bin/setup-db` and follow the instructions. This will create the database, tables, and more.

To setup the test database, run `EAVE_ENV=test bin/setup-db`