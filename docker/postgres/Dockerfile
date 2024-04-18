FROM postgres:alpine

RUN mkdir -p /docker-entrypoint-initdb.d
COPY ./docker/postgres/docker-entrypoint-initdb.d/* /docker-entrypoint-initdb.d/

EXPOSE 5432