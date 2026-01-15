#! /usr/bin/env python3

import argparse

def _parse_arguments() -> argparse.Namespace:
    """
        Parses command line arguments.

        Mandatory arguments:
            - Compound list: main input file. Consists of a list of compounds, one per line.
            - Annotation: SQLite db file containing annotation.
            - Background: List of background compounds, one per line.
            - Output: Path to output file.
            - 

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser("mbRole")
    parser.add_argument("--compound","-i", type=argparse.FileType('r'), help="Path to a file containing a set of compounds. One compound per line.", required=True)
    parser.add_argument("--db_file","-dbf", type=str, help="Path to a SQLite database file containing annotation.", required=True)
    parser.add_argument("--annotation","-a", nargs="*", type=str, help="Annotation to make the enrichment analysis to", default="")
    parser.add_argument("--background","-bg", type=argparse.FileType('r'), help="(Optional) Path to a file containing background compounds. One compound per line. If no value indicated, the compouns on all annotation sets will be used as background", required=False)
    parser.add_argument("--database", "-db", type=str, nargs="+", help="Database from which the annotations are used, stored in db. More than one can be used. Non case sensitive", required=True)
    parser.add_argument("--loglevel", "-l", type=str, choices=["debug","info","warning","error","critical"], help="Miminal log level to report", default="info")
    parser.add_argument("--logfile", "-lf", type=str, help="File path to store logs")
    return parser.parse_args()