#! /usr/bin/env python3

"""
    This script parses the kegg compound files and makes a list of categories
    and the compounds that form those categories for its use with mbRole.

    Note that I have had some problems with the original compound.txt.gz file, as
    detected some charachters as non utf-8 (because it was not utf-8). I converted it to utf-8
    to avoid this but now I wonder wether I should take it into account in every script

    TODO: Add file encoding support to avoid this
"""

import argparse
import collections
import logging
import gzip

logging.basicConfig(level=logging.WARN)

def _parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i", type=str, help="Path to KEGG compound file", required=True)
    parser.add_argument("--output","-o", type=str, help="Output DB to save Kegg data")
    return parser.parse_args()

def parse_kegg(file:str) -> list:
    """
        Kegg Compound file has a particular layout, but in general, is a space-separated column file.
        Note that the values may have spaces in names or value, so parsing must have that into account

        The first column is mostly empty, but their elements indicate the start of the next section, e.g:

        ENTRY   CXXXXX1
        NAME    Sodium Chlorure
        PATHWAY MPXXXX1
                MPXXXX2
                MPXXXX3
        OTHER   We don't care about other sections

        In this case: the KEGG ID is the ENTRY, CXXXX1NAME should be considered "Sodium Chlorure" and PATHWAY should be a list [MPXXXX1, MPXXXX2, MPXXXX3]
    """
    openf = gzip.open if file.endswith(".gz") else open
    with openf(file, "rt") as fhand:
        compounds = collections.defaultdict(list)
        pathways = False
        ID = ""
        for line in fhand:
            if (line.startswith("ENTRY")):
                # Remember: Names may have spaces
                ID = line.strip("\n").strip(";").split()[1]
            elif line.startswith("PATHWAY"):
                elements = line.strip("\n").split()
                logging.debug(elements)
                pathways = True
                # Pathway names have spaces inside name
                data = (elements[1], " ".join(elements[2:]))
                logging.info(f"{ID}, {data}")
                if(ID):
                    compounds[ID].append(data)
            # Remember: section header only appears once, so until
            # We reached the next section (MODULE), we continue parsing 
            # Pathways
            elif not line.startswith(" "):
                pathways = False
            elif (pathways):
                line = line.strip("\n").split()
                logging.info(f"{ID}, {line[0]}, {" ".join(line[1:])}")
                data = (line[0], " ".join(line[1:]))
                compounds[ID].append(data)               
    return compounds

def main():
    args = _parse_args()
    data = parse_kegg(args.input)
    #print("Compound","Pathway","DDBB","link")
    i = 1
    for key in data:
        pathways = data[key]
        for pathway in pathways:
            print(f"{key},\"{pathway[1]}\",KEGG,False")
            i += 1

if __name__=="__main__":
    main()