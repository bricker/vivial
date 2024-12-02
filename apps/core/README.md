## Database

It is recommended to run a local Postgres server for development.

### Postgres installation and setup

This is very OS-specific and there are many options. Find your OS [here](https://www.postgresql.org/download/) and follow the instructions.

In addition, [PostGIS](https://postgis.net/) is a required extension. OS-specific installation instructions can be found [here](https://postgis.net/documentation/getting_started/).

The goal is to have a Postgres server running locally, with the PostGIS extension installed. There are many tutorials on the internet that you can follow to accomplish this.

#### macOS

On macOS, [Postgres.app](https://postgresapp.com/) is recommended. It has everything you need, _including PostGIS_, and it automatically creates a default admin user for you. Download and run it and you should be good to go.

#### Ubuntu

On Ubuntu, Postgres comes pre-installed, but may not be the latest version. See [here](https://www.postgresql.org/download/linux/ubuntu/) for how to download the latest version. Once installed, these are some useful commands to get setup:

```sh
# Install postgis
sudo apt install postgresql-16-postgis-3

# Start postgres
sudo service postgres start

# Create a postgres user
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

Run `bin/setup-db-dev` and follow the instructions. This will create the database, tables, and more.

To setup the test database, run `EAVE_ENV=test bin/setup-db-dev`
