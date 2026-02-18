#! /usr/bin/env python3

import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i", nargs="+")
    return parser.parse_args()

def main():
    args = parse_args()
    for element in args.input:
        with open(element) as fhand:
            for line in fhand:
                if line.startswith("circ"):
                    line:list = line.strip("\n").split()
                    compound:str = line[4]
                    print(compound)

if __name__ == "__main__":
    main()