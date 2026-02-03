#! /usr/bin/env python3

import numpy as np
import scipy
import scipy.stats
import sqlite3

import logging
import collections


def get_category_compounds(conn: sqlite3.Connection, category: str) -> list[str]:
    SQL = f"SELECT compound FROM mbrole WHERE annotation=\"{category}\""
    cursor = conn.cursor()
    cursor.execute(SQL)
    return {x[0] for x in cursor.fetchall()}

def get_all_categories_from_db(conn: sqlite3.Connection, table:str):
    SQL = f"SELECT DISTINCT annotation FROM {table};"
    logging.debug(SQL)
    cursor = conn.cursor()
    cursor.execute(SQL)
    return [x[0] for x in cursor.fetchall()]

def get_categories_from_db(conn: sqlite3.Connection, table: str, db:str, annotation:str) -> set:
    SQL = f"SELECT compound FROM {table} WHERE database=\"{db}\" AND annotation=\"{annotation.lower()}\";"
    logging.debug(SQL)
    cursor = conn.cursor()
    cursor.execute(SQL)
    return {x[0] for x in cursor.fetchall()}

def get_genes_per_category(conn, table, db):
    SQL = f"SELECT * FROM {table} WHERE database=\"{db}\";"
    logging.debug(SQL)
    cursor = conn.cursor()
    cursor.execute(SQL)
    categories = collections.defaultdict(list)
    for compound in cursor.fetchall():
        logging.debug(compound)
        categories[compound[1]].append(compound[0])
    return categories

def get_background_genes_from_db(conn: sqlite3.Connection, table:str, db: str):
    """
        
    """
    SQL = f"SELECT compound FROM {table} WHERE database=\"{db}\""
    cursor = conn.cursor()
    cursor.execute(SQL)
    return {x[0] for x in cursor.fetchall()}


def functional_enrichment(genes_in_query: set, genes_in_category:set, background:set) -> float:
    """
        Perfoms a fisher test to execute the functional enrichment analysis

        Returns uncorrected p-value
    """
    logging.debug(f"Genes in query: {genes_in_query}")
    logging.debug(f"Genes in category: {genes_in_category}")
    genes_from_query_in_set = len(genes_in_query.intersection(genes_in_category))
    if(genes_from_query_in_set == 0):
        # No genes in query, skipping
        return 1, genes_from_query_in_set, len(genes_in_category)
    logging.debug(f"Genes in query in set: {genes_from_query_in_set}")
    genes_from_query_not_in_set = len(genes_in_query.difference(genes_in_category))
    logging.debug(f"Genes in query not in set: {genes_from_query_not_in_set}")
    genes_from_background_in_set = len(background.intersection(genes_in_category))
    logging.debug(f"Genes in background in set: {genes_from_background_in_set}")
    genes_from_background_not_in_set = len(background.difference(genes_in_category))
    logging.debug(f"Genes in background not in set: {genes_from_background_not_in_set}")
    table = np.array([genes_from_query_in_set, genes_from_background_in_set, genes_from_query_not_in_set, genes_from_background_not_in_set]).reshape((2,2))
    logging.debug(f"Data for T-test: {table}")
    pval = scipy.stats.fisher_exact(table)
    return pval.pvalue, genes_from_query_in_set, len(genes_in_category)

def correct_pvalue(pvalues):
    return scipy.stats.false_discovery_control(pvalues, method="bh")