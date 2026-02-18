#! /usr/bin/env python3 

"""
    Reactome to SQLite

    This script parses a Reactome .txt file and inserts the data into a SQLite database
    for mbRole analysis.

    Usage:
        python reactome.py <reactome_txt_file> <db_sqlite_file> db 
"""

import argparse
import logging
import os

import sqlite3

def initialize_logger(default_logging_level: str) -> logging.Logger:
    logging_level:str = 0
    match default_logging_level:
        case "debug": 
            logging_level = logging.DEBUG
        case "info": 
            logging_level = logging.INFO
        case "warning": 
            logging_level = logging.WARNING
        case "error": 
            logging_level = logging.ERROR
        case "critical": 
            logging_level = logging.CRITICAL
    logger: logging.Logger = logging.getLogger("Reactome")
    logging.basicConfig(level=logging_level)
    return logger


def _parse_args() -> argparse.Namespace:
    parser:argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--reactome", "-i", required=True)
    parser.add_argument("--file", "-o", required=True)
    parser.add_argument("--db_name","-db",required=True)
    parser.add_argument("--log_level","-l", type=str, default="info", choices=["debug","info","warning","error","critical"])
    parser.add_argument("--table_name","-t", type=str, default="mbrole")
    return parser.parse_args()

def initialized_db(file: str) -> bool:
    """
        Checks whether the database file:
        - exists
        - is a file
        - is a valid SQLite database
    """
    if (not os.path.exists(file)):
        return False
    if (not os.path.isfile(file)):
        return False
    return True

def initialize_db(file: str, table_name:str) -> int:
    with sqlite3.connect(file) as conn:
        conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, annotation VARCHAR(50), database VARCHAR(20) );")
        conn.commit()
    return 0

def connect_to_db(file: str, db:str) -> sqlite3.Connection:
    pass

def parse_reactome(file: str):
    with open(file) as fhand:
        for line in fhand:
            line = line.strip("\n")
            data = line.split("\t")
            yield (data[0], data[1], "reactome")
    pass

def main() -> None:
    args: argparse.Namespace = _parse_args()
    logger: logging.Logger = initialize_logger(args.log_level)
    if (not initialized_db(args.file)):
        logger.info(f" Database {args.file} does not exist. Initializing database with table name {args.db_name}.")
        initialized_db(args.file)
    parse_reactome
    pass

if __name__ == "__main__":
    main()