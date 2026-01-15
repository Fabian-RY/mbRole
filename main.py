#! /usr/bin/env python3

import logging
import sqlite3
import sys

import numpy as np
import tqdm

import mbrole.arg_parse
import mbrole.functional_enrichment

def get_bg_set(bg_arg:str, db:str) -> list:
    if bg_arg:
        return parse_input_file(bg_arg)
    return mbrole.functional_enrichment.get_background_genes_from_db(sqlite3.Connection(db), "mbrole", "CHEBI")

def parse_input_file(file:str) -> set:
    compounds = {}
    with file as fhand:
        compounds = fhand.readlines()
        compounds = set(map(lambda x: x.strip(), compounds))
    return compounds

def set_logger(name:str, file:str, log_level:int):
    match log_level:
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
    if file is None:
        handlers=[logging.StreamHandler()]
    else:
        handlers=[logging.StreamHandler(),
                  logging.FileHandler(file)]
    logging.basicConfig(handlers=handlers,
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging_level)
    return logging.getLogger(name)

def _perform_FE(category, query_set, bg_set, annotation):
    #annotation = mbrole.functional_enrichment.get_categories_from_db(conn, table, db, category)
    logging.debug(f"Performing FE for {annotation} with query {query_set}")
    return np.array([category, mbrole.functional_enrichment.functional_enrichment(query_set, annotation, bg_set)])

def main():
    args = mbrole.arg_parse._parse_arguments()
    logger = set_logger("mbrole-cli", args.logfile, args.loglevel)
    logger.info("Welcome to Mbrole-CLI")
    logger.info("Parsing input file")
    query_set = parse_input_file(args.compound)
    if len(query_set) == 0:
        logger.error(f"Empty input file: {args.compound}")
        sys.exit(1)
    logger.info(f"Query set parsed: Detected {len(query_set)} compounds")
    logger.info(f"Compounds detected: {query_set}")
    categories = args.annotation
    logger.info(f"Categories selected: {categories}")
    if len(categories) == 0:
        logger.info("No categories selected: Using full database")
        categories = mbrole.functional_enrichment.get_genes_per_category(sqlite3.Connection(args.db_file), "mbrole","CHEBI")
    else:
        categories = {x:mbrole.functional_enrichment.get_category_compounds(sqlite3.Connection(args.db_file), x) for x in categories}
    logger.info(f"Analyzing {len(categories)} categories")
    bg_set = get_bg_set(args.background, args.db_file)
    
    result = list(map(lambda x: _perform_FE(x, query_set, bg_set, categories[x]), tqdm.tqdm(categories.keys())))
    logging.info(result)
        
if __name__ == "__main__":
    main()
