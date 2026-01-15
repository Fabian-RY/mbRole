#! /usr/bin/env python3 

"""
    Reactome to SQLite

    This script parses a Reactome .txt file and inserts the data into a SQLite database
    for mbRole analysis.

    Usage:
        python reactome.py <reactome_txt_file> <db_sqlite_file> db 
"""

import argparse
import gzip
import json
import logging
import os

import sqlite3
import tqdm

def _parse_CHEBI_id_from_url(url: str) -> str:
    """
        Chebi id field is the url, of which the endpoint is the
        CHEBI:XXXXXX id.
    """
    return url.split("/")[-1]

def initialize_logger(default_logging_level: str) -> logging.Logger:
    """
        Start the logging system

        The goal is to have one logger per database, so parallel works can be done.

        Each logger should be identified properly and the database which the thread is parsing. Each logger
        may have different logging level.
    """
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
    logger: logging.Logger = logging.getLogger("Chebi")
    logging.basicConfig(level=logging_level)
    return logger


def _parse_args() -> argparse.Namespace:
    parser:argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("--chebi", "-i", required=True)
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
    # Todo: Check if valid SQLite database
    # and table exist
    return True

def initialize_db(file: str, table_name:str) -> int:
    """
        Creates the SQLite file and the table for mbrole
        The table has these columns:
            - compound: the name of the compound. For testing purposes, max length is 20.
            - annotation: the field to which the compound is part of, for the enrichment analysis.
            - database: the source for the compound name and annotation
            - URL: officuak URL for compound info,
    """
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (compound VARCHAR(20), annotation VARCHAR(50), database VARCHAR(20), URL VARCHAR(100) );")
    conn.close()
    return 0 # 0 means success. It does not check if the file cannot exist, as the function initialized_db checked that.

def load_chebi_data(file:str):
    """
        Loads the chebi ontology from th official JSON file from: https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/
        As it can be either json, or json.gz, the correct function is determined according to the file extension.

        IMPROVEMENT TODO: check mimetype instead and handle errors accordingly.
    """
    open_function = gzip.open if file.endswith(".json.gz") else open
    fhand = open_function(file, 'rt')
    return json.load(fhand)

def parse_chebi(data: str) -> tuple[str,str]:
    """
        Parses the preloaded chebi data. Gets 2 fields:
        - sub: ID of a compound
        - obj: ID of a category to which sub is ontologically related.

        TODO: 
            - keep the type of relation they have (E.j: is_a, has_role, etc)
            - Maybe it would be faster if data was only the relations that is calculated
            on the first line of the function.
    """
    relations = data["graphs"][0]["edges"]
    for relation in relations:
        sub, obj = _parse_CHEBI_id_from_url(relation["sub"]), _parse_CHEBI_id_from_url(relation["obj"])
        yield (sub, obj)

def _get_obj_name(chebi_id: str, chebi_data:dict) -> dict:
    """
        Filters the whole chebi data, to get just the node with the given id.

        Then, returns the label. 
        
        TODO: Note that the label is not guaranteed to exist, but in practice,
        exists for all categories or compounds we need
    """
    node = next(filter(lambda x: x["id"] == f"http://purl.obolibrary.org/obo/{chebi_id}", chebi_data))
    return node["lbl"]

def _get_chebi_nodes(chebi_data: dict) -> dict[str, str]:
    nodes = chebi_data["graphs"][0]["nodes"]
    chebi_nodes: dict[str, str] = {}
    for node in nodes:
        chebi_id = _parse_CHEBI_id_from_url(node["id"])
        if ("lbl" in node):
            chebi_nodes[chebi_id] = (node["lbl"], node["id"])
        else: 
            continue
    return chebi_nodes

def insert_into_db(table_name: str, compound: str, annotation: str, database: str, url: str, connection:sqlite3.Connection) -> None:
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO {table_name} (compound, annotation, database, URL) VALUES (?, ?, ?, ?);", (compound, annotation, database, url))
    connection.commit()
    cursor.close()

def main() -> None:
    args: argparse.Namespace = _parse_args()
    logger: logging.Logger = initialize_logger(args.log_level)
    if (not initialized_db(args.file)):
        logger.info(f" Database {args.file} does not exist. Initializing database with table name {args.db_name}.")
        initialize_db(args.file, args.db_name)
    logger.info(f" Loading ChEBI data from {args.chebi}.")
    chebi_data = load_chebi_data(args.chebi)
    chebi_nodes = _get_chebi_nodes(chebi_data)
    logger.info("Loaded chebi data")
    parsed_data = list(parse_chebi(chebi_data))
    logger.info(f"Parsed {len(parsed_data)} relations from ChEBI data.")
    connection = sqlite3.connect(args.file)
    for sub, obj in tqdm.tqdm(parsed_data):
        obj, obj_url = chebi_nodes[obj]
        sub, sub_url = chebi_nodes[sub]
        logger.debug(f"Obtained relation: {sub} -> {obj}")
        logger.debug(f"Inserting relation: {sub} -> {obj} into database {args.file}.")
        insert_into_db(args.db_name, sub, obj, "CHEBI", sub_url, connection)

if __name__ == "__main__":
    main()