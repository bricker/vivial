# PostgreSQL Database atom collector

Uses the LISTEN/TRIGGER API in PostgreSQL to receive notifications on any INSERT, UPDATE, or DELETE operations.
It then constructs a raw atom payload, and sends it via HTTPS to the Eave backend for further processing.

## Dev setup

Get going with a simple `make` command. That will build the agent, putting the executable in the `build/` directory (along
with a bunch of build artifact garbage you can ignore).

### Dependencies

Some libc implementation required.

The full `postgres` dependency must be installed (on the compiling machine) such that pgsql can be found at the
path `/usr/local` (and therefore the contained libpq static library). The program
cannot compile without this dependency, as we rely on the libpq C api that is part of the `postgres` distribution.
The version of `postgres` must be 12 or higher, as that is when the LISTEN/TRIGGER API was introduced.

libcurl is required for our networking code. Having the `curl` command line tool installed will provide a
dynamic library to link against.

## TODO down the line

* find a way to compile against static libs for curl and postgres so we dont have to install their dylibs in docker for binary to work
* probs want some pre-processing to make sure we dont send sensitive info to eave backend (if possible)
