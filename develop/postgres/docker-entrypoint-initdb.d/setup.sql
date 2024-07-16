CREATE USER app WITH PASSWORD 'unsafe';

CREATE DATABASE "eave-development";
ALTER DATABASE "eave-development" OWNER TO app;

CREATE DATABASE "metabase-development";
ALTER DATABASE "metabase-development" OWNER TO app;
