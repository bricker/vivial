## Install Requirements

SQL Proxy.

https://cloud.google.com/sql/docs/postgres/sql-proxy#install

```
wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
```

Switch to Python 3.10 (pyenv recommended).

```
pyenv shell 3.10
```

Install Python requirements (in a vritual env if u wanna).

```
pip install -r requirements.txt
```

Aquire a `.env` file from someone on the team.


## Local Development

Start Uvicorn.

```
uvicorn main:app --reload
```

Run CloudSQL proxy.

```
./cloud_sql_proxy -dir /tmp/cloud_sql
```

Make requsts to the API (you can use curl or something like Postman).

```
curl -H "Content-Type:application/json" http://127.0.01:8000/access_request -d '{"email": "test"}'
```

## Deploying the App

```
gcloud app deploy
```
