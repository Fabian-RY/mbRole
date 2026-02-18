#! /usr/bin/env python3

import argparse
import sqlite3

import pandas as pd
import tqdm

def _parse_args() -> argparse.ArgumentParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--input","-i", help="CTD csv file downloaded from the official repository")
    parser.add_argument("--header","-hd", help="Row in which data starts", default=30)
    parser.add_argument("--output","-o", help="Path to the desired sqlite db file to store data")
    parser.add_argument("--table","-t", help="table of the DB in which store the info")
    parser.add_argument("--db_name","-db", help="Where the data comes from")
    return parser.parse_args()

def _save_to_sqlite(conn, table, id, name, db, url, category):
    SQL = f"INSERT INTO {table} (compound, annotation, database, url) VALUES  (\"{id}\", \"{name}\", \"{db}\", \"{url}\");"
    cursor = conn.cursor()
    cursor.execute(SQL)
    conn.commit()
    cursor.close()

def main() -> None:
    args = _parse_args()
    data = pd.read_csv(args.input, sep=",", header=args.header)
    conn = sqlite3.Connection(args.output)
    for i in tqdm.tqdm(list(data.itertuples())):
        _save_to_sqlite(conn, args.table, i[2], i[4], args.db_name, i[2], "")
    pass

if __name__=="__main__":
    main()