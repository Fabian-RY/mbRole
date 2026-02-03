#! /usr/bin/env python3

import logging
import sqlite3
import sys

import numpy as np
import pandas as pd
import scipy
import tqdm

import mbrole.arg_parse
import mbrole.functional_enrichment

def get_bg_set(bg_arg:str, db:str) -> list:
    if bg_arg:
        return parse_input_file(bg_arg)
    return mbrole.functional_enrichment.get_background_genes_from_db(sqlite3.Connection(db), "mbrole", "CHEBI")

def parse_input_file(file:str) -> set:
    compounds: set = {}
    with open(file) as fhand:
        compounds:str = fhand.readlines()
        compounds:set = set(map(lambda x: x.strip(), compounds))
    return compounds

def set_logger(name:str, file:str, log_level:int) -> logging.Logger:
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
        handlers:list =[logging.StreamHandler()]
    else:
        handlers:list =[logging.StreamHandler(),
                  logging.FileHandler(file)]
    logging.basicConfig(handlers=handlers,
                    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging_level)
    return logging.getLogger(name)

def _perform_FE(category: set, query_set:set, bg_set:set, annotation:str) -> float:
    #annotation = mbrole.functional_enrichment.get_categories_from_db(conn, table, db, category)
    logging.debug(f"Performing FE for {annotation} with query {query_set}")
    res = mbrole.functional_enrichment.functional_enrichment(query_set, annotation, bg_set) 
    if (res is None):
        return
    pval, in_set, in_annotation = res
    return pval, in_set, in_annotation

def main():
    args = mbrole.arg_parse._parse_arguments()

    # Setting up logger for mbrole-cli
    logger:logging.Logger = set_logger("mbrole-cli", args.logfile, args.loglevel)
    logger.info("Welcome to Mbrole-CLI")
    logger.info("Parsing input file")

    # Parse input set. Note that if the file is empty
    # There's no reason to continue. So the user is warned
    # and the program exits
    query_set:set = parse_input_file(args.compound)
    if len(query_set) == 0:
        logger.error(f"Empty input file: {args.compound}")
        sys.exit(1)
    logger.info(f"Query set parsed: Detected {len(query_set)} compounds")
    logger.info(f"Compounds detected: {query_set}")

    # Now we parse the categories providen, which can be from 0 to as many as the user wants
    # If no values are provided, takes ALL annotations of the databases, so user does not have to specify it
    # By providing a DB, only annotations that were obtained from that database will be used
    # (And by DB I mean CHEBI, KEGG, ECMDB, HMDB, YMDB, etc)
    categories:list = args.annotation
    logger.info(f"Categories selected: {categories}")
    if len(categories) == 0:
        logger.info("No categories selected: Using full database")
        logger.info(f"database selected {args.database}")
        annotation:dict = dict()
        databases:list = args.database
        logging.debug(type(databases), databases)
        if databases == []: 
            databases:list = mbrole.annotation.get_categories_from_db(args.db_file, args.table) # No database indicated, using all of them
            logging.debug(type(databases), databases)
        logger.info("Consolidating annotations")
        # We want to merge the annotations from different databases
        # That are available in the database. 
        for category in tqdm.tqdm(databases):
            ann_ = mbrole.functional_enrichment.get_genes_per_category(sqlite3.Connection(args.db_file), args.table, category)
            annotation = annotation | ann_ # This is a set union operator. It works for dicts as well as keys behave as sets
    else:
        # As we have the annotations of interest, we just query them
        # A dict comprehension is easy to set up
        annotation = {x:mbrole.functional_enrichment.get_category_compounds(sqlite3.Connection(args.db_file), x) for x in categories}

    logger.info(f"Analyzing {len(annotation)} categories")

    # Now we need to get the background set. The get_bg_set either parses the file given or uses the FULL SQLITE DATABASE as background
    # This were the available possibilites at mbRole 3, so I kept them
    # TODO: Add species particular sets, as a variation of providing a file
    bg_set:set = get_bg_set(args.background, args.db_file)

    # Performing the FE
    #result = list(map(lambda x: _perform_FE(x, query_set, bg_set, annotation[x]), tqdm.tqdm(annotation.keys())))
    result: list = list()
    for annotation_name in tqdm.tqdm(annotation.keys()):
        pval, in_set, in_annotation = _perform_FE(annotation_name, query_set, bg_set, annotation[annotation_name])
        if (pval is None):
            pval = 1
        result.append((annotation_name, pval, in_set, in_annotation))
    df = pd.DataFrame(result, columns=["name","pval","Compund-in-set","Compound-in-annotation"])
    df["FDR"] = scipy.stats.false_discovery_control(df["pval"])
    if (not args.all):
        df = df[df["FDR"] < 0.05]
    df.to_csv(args.output)


        

if __name__ == "__main__":
    main()
