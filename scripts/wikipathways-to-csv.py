#! /use/bin/env python3

"""

    Parses Wikipathways xml files

"""

import argparse
import os
import xml.etree.ElementTree as ET

def parseargs():
    """
        Parses arguments: establishes an interface with 3 arguments for CLI

        Folder: input folder where wikipathways are stored
        Output: Output file to save the data. Default is standard output
        Category: Category to filter elements in the pathway. By default no filtering is done.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", "-i", required=True, help="Folder where WikiPathways xml files are stored")
    parser.add_argument("--output","-o", default="/dev/stdout", help="File to save parsed data. By default prints to stdout")
    parser.add_argument("--category","-c", default=None, help="Filter Nodes by category")
    return parser.parse_args()

def parse_file(file:str, category:str=None):
    XML = ET.parse(file)
    pathway = XML.getroot().attrib["Name"]
    molecules = []
    for node in XML.getroot():
        if not node.tag.endswith("DataNode"):
            continue
        if (category and "Type" in node.attrib and category != node.attrib["Type"]):
            continue
        molecules.append(node.attrib["TextLabel"])
    return pathway, molecules

def main():
    args = parseargs()
    files = os.listdir(args.folder)
    data = [parse_file(f"{args.folder}/{x}", category=args.category) for x in files]
    fout = open(args.output, "wt")
    for pathway, molecules in data:
        for molecule in molecules:
            molecule = " ".join(molecule.strip("\n").split()) # For some reason some spaces are interpreted as new lines
            print(f"\"{molecule}\",\"{pathway}\",\"Wikipathways\",\"WikiPathWays\"", file=fout)


if __name__=="__main__":
    main()
