# Eave Web App

[https://www.eave.fyi/](https://www.eave.fyi/)

## Running the Marketing App Using VS Code

1. Run the HTTP proxy from the root directory.
```
bin/http-proxy
```

2. Open the Run & Debug panel in VS Code and select either "Marketing Website" or "Core API + Marketing Website" in the dropdown menu.

3. Click the play button located next to the dropdown menu.

4. Now you should be able to access the marketing website at https://www.eave.run:8080/


## Connecting to Prod Database

Cloud SQL Proxy
```
./cloud_sql_proxy -dir=/tmp/cloudsql --instances=eave-production:us-central1:eave-development
```

Postgres [pgAdmin](https://www.pgadmin.org/)
```
psql --host=/tmp/cloudsql/eave-production\:us-central1\:eave-development/ --username=<username> -d eave
```