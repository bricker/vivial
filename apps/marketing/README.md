# Eave Web App

[https://www.eave.fyi/](https://www.eave.fyi/)

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

4. Open the Run & Debug panel in VS Code and select "Core API + Marketing Website" in the dropdown menu.

5. Click the play button located next to the dropdown menu.

6. Access the marketing website at https://www.eave.run:8080.
