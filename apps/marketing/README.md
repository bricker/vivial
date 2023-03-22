# Eave Web App

[https://www.eave.fyi/](https://www.eave.fyi/)

## Connecting to Prod Database

Cloud SQL Proxy
```
./cloud_sql_proxy -dir=/tmp/cloudsql --instances=eave-production:us-central1:eave-development
```

Postgres [pgAdmin](https://www.pgadmin.org/)
```
psql --host=/tmp/cloudsql/eave-production\:us-central1\:eave-development/ --username=<username> -d eave
```