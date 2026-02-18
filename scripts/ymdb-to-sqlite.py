#! /usr/bin/env python3

import argparse
import json
import sqlite3

import tqdm


def parse_args():
    parser: argparse.ArgumentParser = argparse.ArgumentParser("YMDB")
    parser.add_argument("--input","-i")
    parser.add_argument("--db_name","-db")
    parser.add_argument("--db_table","-t")
    parser.add_argument("--id_tag","-id")
    parser.add_argument("--output","-o")
    return parser.parse_args()

def parse_ymdb(file: str):
    data = json.load(open(file))
    for key in data:
        yield key

def _save_to_sqlite(conn, table, id, name, db, url, category):
    SQL = f"INSERT INTO {table} (compound, annotation, database, url) VALUES  (\"{id}\", \"{name}\", \"{db}\", \"{url}\");"
    cursor = conn.cursor()
    cursor.execute(SQL)
    conn.commit()
    cursor.close()

def main():
    args = parse_args()
    conn = sqlite3.Connection(args.output)
    for compound in tqdm.tqdm(list(parse_ymdb(args.input))):
        if "pathways" in compound and compound["pathways"]:
            pathways = compound["pathways"]
            for pathway in pathways:
                _save_to_sqlite(conn, args.db_table, compound[args.id_tag], pathway["name"], args.db_name, compound[args.id_tag], f"{args.db_name}_pathways")
        if "location" in compound and compound["location"]:
            location = compound["location"]
            if(";" in compound["location"]):
                # A single element may have many different locations
                location = location.split(";")
            else:
                location = [location]
            for element in location:
                _save_to_sqlite(conn, args.db_table, compound[args.id_tag], element, args.db_name, compound[args.id_tag], f"{args.db_name}_location")
    conn.close
    

if __name__=="__main__":
    main()
    pass