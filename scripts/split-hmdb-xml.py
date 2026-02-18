#! /usr/bin/env python3

import argparse
import gzip
import logging
import os
import tqdm

logging.basicConfig(level=logging.INFO)

def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input","-i")
    parser.add_argument("--output","-o")
    parser.add_argument("--chunksize","-c", type=int)
    return parser.parse_args()

if __name__=="__main__":
    args = _parse_args()
    file = 0
    metabolites = 0
    text = ""
    if (not os.path.exists(args.output)): 
        os.mkdir(args.output)
    for line in open(args.input):
        text += line
        if line.startswith("<metabolite>"):
            #logging.info("New metabolite found")
            metabolites += 1
        if line.startswith("</metabolite>") and metabolites == args.chunksize:
            filename = f"chunks_{args.chunksize}_{file}"
            file += 1
            with gzip.open(f"{args.output}/{filename}", "wt") as fhand:
                fhand.write(text)
            metabolites = 0
            text = ""
        print(f"Current files saved: {file}, chunksize: {args.chunksize}, current metabolites parsed for next file: {metabolites} ", end="\r")