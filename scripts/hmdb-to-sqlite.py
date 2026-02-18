#! /usr/bin/env python3

import argparse
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.DEBUG)

def save_to_sqlite(data, sqlite_path, db, table):
    pass

def _parse_xml(file: str, namespace="http://www.hmdb.ca") -> list:
    logging.info("Loading HMDB XML tree...")
    data = ET.iterparse(open(file))
    logging.info("Loaded XML tree")
    for event, element in data:
        if("metabolite" in element.tag):
            print("metabolite")

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i")
    parser.add_argument("--output","-o")
    parser.add_argument("--database","-db")
    parser.add_argument("--table","-t")
    return parser.parse_args()

def main():
    args = _parse_args()
    metabolites = _parse_xml(args.input)
    save_to_sqlite(metabolites, args.output, args.db, args.table)


if __name__=="__main__":
    main()