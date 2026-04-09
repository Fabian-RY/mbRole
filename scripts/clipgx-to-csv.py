#! /usr/bin/env python3

import sys

import json

def main():
    pathway_file = json.load(open(sys.argv[1]))
    outfile = sys.argv[2] if len(sys.argv) > 2 else "/dev/stdout"
    for pathway in pathway_file:
        id = pathway["id"]
        name = "".join(pathway["name"].split(",")[0])
        molecules = [x["id"] for x in pathway["chemicals"]]
        for x in molecules:
            print(f"\"{x}\",\"{id}\",\"{name}\",\"ClinPGX\",\"null\"") 

if __name__ == "__main__":
    main()