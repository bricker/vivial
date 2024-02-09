import asyncio
import argparse
import subprocess
import sys
import os
from typing import Optional
import psycopg
from psycopg import sql

# num ops to perform per operation type (insert/update/delete)
NUM_ROW_OPS = 100


async def build_tables(session: psycopg.AsyncConnection) -> list[str]:
    """returns list of created table structs"""
    return []


async def drop_tables(session: psycopg.AsyncConnection, tables: list[str]) -> None:
    for table in tables:
        pass


async def populate_tables(session: psycopg.AsyncConnection, tables: list[str]) -> None:
    ops = ["INSERT", "UPDATE", "DELETE"]
    for op in ops:
        for i in range(NUM_ROW_OPS):
            pass


def launch_agent(
    conn: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> subprocess.Popen:
    """returns created agent process"""
    args = []
    if conn:
        args += ["-c", conn]
    else:
        args += ["-d", database]
        args += ["-u", username]
        args += ["-p", password]

    # TODO: point to real bin
    return subprocess.Popen(["../agent.py"] + args)


def print_stats() -> None:
    """prints expected data creation stats from agent (good enough to verify all worked)"""
    print("TODO: stats here")


async def create_connection(
    conn: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> psycopg.AsyncConnection:
    if conn:
        connection = await psycopg.AsyncConnection.connect(conninfo=conn, autocommit=True)
        return connection
    else:
        # try connecting w/ other info
        connection = await psycopg.AsyncConnection.connect(
            database=database,
            user=username,
            password=password,
        )
        return connection


async def main(
    conn: Optional[str],
    database: Optional[str],
    username: Optional[str],
    password: Optional[str],
) -> None:
    db = database or (conn.split("/")[-1] if conn else "unknown")
    answer = input(print(f"Proceed to insert junk seed data into the {db} database? (Y/n) "))
    if answer != "Y":
        print("Aborting.")
        return

    session = await create_connection(conn, database, username, password)

    try:
        tables = await build_tables(session)

        proc = launch_agent(conn, database, username, password)

        await populate_tables(session, tables)

        proc.kill()

        print_stats()

        answer = input(print(f"Proceed to drop the created junk tables in the {db} database? (Y/n) "))
        if answer != "Y":
            print("Aborting.")
            return

        await drop_tables(session, tables)
    finally:
        await session.close()

def parse_args() -> dict[str, str]:
    parser = argparse.ArgumentParser(
        prog="Test program for Eave Postgresql agent",
        description="Populates dummy data in dummy tables, and listens for expected changes",
    )
    parser.add_argument("-d", "--database", help="name of the database to track changes in")
    parser.add_argument("-u", "--username", help="username to connect to db with")
    parser.add_argument("-p", "--password", help="user password to connect to db with")
    parser.add_argument("-c", "--conn", help="database connection string")

    args = parser.parse_args()

    if args.database is None and args.conn is None:
        print("Either the 'database' or 'conn' flag must be provided to this program in order to connect to a database on which to test.")
        sys.exit(1)

    return args.__dict__


if __name__ == "__main__":
    args = parse_args()
    print(args)
    asyncio.run(main(**args))
