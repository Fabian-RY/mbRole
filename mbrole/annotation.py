#! /usr/bin/env python3

import logging
import sqlite3

def get_categories_from_db(db, table):
    SQL = f"SELECT DISTINCT database from {table};"
    logging.debug(SQL)
    conn = sqlite3.Connection(db)
    cursor = conn.cursor()
    cursor.execute(SQL)
    return [x[0] for x in cursor.fetchall()]
