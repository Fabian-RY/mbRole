#! /usr/bin/env python3

"""
    Extracts data needed for mbrole from SMPDB CSV files
"""

import argparse
import logging
import os

import tqdm

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", "-i", required=True)
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--output_names", "-on", required=True)
    parser.add_argument("--converser", "-c", required=True)
    return parser.parse_args()

def main():
    args = parse_args()
    files = os.listdir(args.input)
    with open(args.output, "wt") as writer:
        with open(args.output_names, "wt") as writer_on:
            with open(args.converser, "wt") as conversor:
                for file in tqdm.tqdm(files):
                    with open(os.path.join(args.input, file),"rt") as reader:
                        next(reader) # Remove header
                        for line in reader.readlines():
                            line = line.strip("\n").split(",")
                            print(f"\"{line[3]}\",\"{line[1]}\",\"SMPDB\",\"\"", file=writer)
                            print(f"\"{line[4]}\",\"{line[1]}\",\"SMPDB\",\"\"", file=writer_on)
                            print(f"\"{line[-1]}\",\"{line[-2]}\",\"{line[3]}\",\"SMPDB\"", file=conversor)
                            print(f"\"{line[-1]}\",\"{line[-2]}\",\"{line[4]}\",\"SMPDB\"", file=conversor)
    
    pass

if __name__ == "__main__":
    main()