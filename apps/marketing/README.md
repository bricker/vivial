# Eave Web App

[https://www.eave.fyi/](https://www.eave.fyi/)

## Getting Started

Local development on port 5000 (Flask)

```
npm run start
```

Formatting with Eslint

```
npm run format
```

## Deployment

After setting up the `gcloud` cli, run the following command:

```
npm run deploy
```

## Connecting to Prod Database

Cloud SQL Proxy
```
./cloud_sql_proxy -dir=/tmp/cloudsql --instances=eave-production:us-central1:eave-development
```

Postgres [pgAdmin](https://www.pgadmin.org/)
```
psql --host=/tmp/cloudsql/eave-production\:us-central1\:eave-development/ --username=<username> -d eave
```