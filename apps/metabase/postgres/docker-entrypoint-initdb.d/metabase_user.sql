CREATE USER metabase_app_dev WITH PASSWORD 'unsafe';
CREATE DATABASE metabase_db_dev;
ALTER DATABASE metabase_db_dev OWNER TO metabase_app_dev;
REVOKE ALL ON DATABASE metabase_db_dev FROM public;
