# Eave Dashboard App

[https://dashboard.eave.fyi/](https://dashboard.eave.fyi/)

## Local Development (optimized for VS Code)

1. Run the HTTP proxy from the root directory.

```
bin/http-proxy
```

2. Connect to the Cloud SQL proxy.

```
bin/cloud-sql-proxy
```

3. Run the PostgreSQL shell (if needed). See basic commands [here](https://www.commandprompt.com/education/postgresql-basic-psql-commands/).

```
bin/pg-shell -d <database> -u <username>
```

4. Open the Run & Debug panel in VS Code and select "Core API + Dashboard" in the dropdown menu.

5. Click the play button located next to the dropdown menu.

6. Access the dashboard at https://dashboard.eave.run:8080.
