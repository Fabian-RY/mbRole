#! /usr/bin/env python3

import argparse

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i", help="LM strudcture database file in .sdf format")
    parser.add_argument("--output","-o", help="File to save the categories")
    return parser.parse_args()

def parse_file(sdf):
    ID = ""
    categories = []
    with open(sdf) as fhand:
        for line in fhand:
            if ("$" in line and ID):
                    yield (ID, categories)
                    ID = ""
                    categories = []
            elif "LM_ID" in line:
                ID = next(fhand).strip()
            elif "CATEGORY" in line or "MAIN_CLASS" in line:
                categories.append(next(fhand).strip())


def main():
    args = parseargs()
    data = parse_file(args.input)
    for ID, categories in data:
        for category in categories:
            print(f"{ID},{category},LSMD,None",end="\n")

if __name__=="__main__":
    main()