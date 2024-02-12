import asyncio
import argparse
import subprocess
import sys
import urllib3 as ul
import os
import random
from typing import Optional
import psycopg
from psycopg import sql

WORD_LIST = ul.request("GET", "https://www.mit.edu/~ecprice/wordlist.10000").data.decode("utf-8").split()

# num ops to perform per operation type (insert/update/delete)
NUM_ROW_OPS = 100
NUM_TABLES = 5
NUM_COLS_MIN = 2
NUM_COLS_MAX = 10
OP_LIST = ["INSERT", "UPDATE", "DELETE"]

class Column:
    def __init__(self, name: str, type: str):
        self.name = name
        self.type = type

    def formated(self) -> str:
        return f"{self.name} {self.type}"
    
    @staticmethod
    def randName() -> str:
        return WORD_LIST[random.randint(0, len(WORD_LIST)-1)]
    
    @staticmethod
    def randType() -> str:
        # TODO: vary the types? then we'll need to update rand insert generation logic. probably make a type enum to switch generation function on
        return "varchar(255)"


class Table:
    def __init__(self, name: str, cols: list[Column]):
        self.name = name
        self.columns = cols

    def formatCols(self) -> str:
        """return cols list as a string of comma separated column names + types (for use in SQL queries)"""
        return ", ".join(map(lambda c: c.formated(), self.columns))

    @staticmethod
    def randName() -> str:
        return WORD_LIST[random.randint(0, len(WORD_LIST)-1)]
    

async def build_tables(session: psycopg.AsyncConnection) -> list[Table]:
    """returns list of created table structs"""
    tables = []

    n_cols = random.randint(NUM_COLS_MIN, NUM_COLS_MAX)

    for _ in range(NUM_TABLES):
        tables.append(
            Table(
                name=Table.randName(),
                cols=[Column(
                    name=Column.randName(),
                    type=Column.randType(),
                ) for _ in range(n_cols)]
            )
        )

    async with session.cursor() as curs:
        for table in tables:
            await curs.execute(
                sql.SQL(
                    "CREATE TABLE {table} ({cols})"
                ).format(
                    table=table.name,
                    cols=table.formatCols(),
                )
            )

    return tables


async def drop_tables(session: psycopg.AsyncConnection, tables: list[Table]) -> None:
    async with session.cursor() as curs:
        for table in tables:
            await curs.execute(
                sql.SQL("DROP TABLE {table}").format(
                    table=sql.Identifier(table.name),
                )
            )


async def populate_tables(session: psycopg.AsyncConnection, tables: list[Table]) -> None:
    for op in OP_LIST:
        for i in range(NUM_ROW_OPS):
            # async w/ inside so that each op is executed separately rather than in 1 commit
            # since real usage wont be in big single commits; they'll be mostly 1-off operations
            async with session.cursor() as curs:
                # TODO: but the ops all have diff command structure??
                await curs.execute(
                    sql.SQL("{op} ").format(
                        op=op,
                    )
                )


def print_stats() -> None:
    """prints expected data creation stats from agent (good enough to verify all worked)"""
    # TODO: aaa
    for op in OP_LIST:
        print(f"Peformed {NUM_ROW_OPS} {op} operations")


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
        print(
            "Either the 'database' or 'conn' flag must be provided to this program in order to connect to a database on which to test."
        )
        sys.exit(1)

    return args.__dict__


if __name__ == "__main__":
    args = parse_args()
    print(args)
    asyncio.run(main(**args))
