#! /usr/bin/env python3

import pytest
import os
import os.path
import sys

main_path=os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, main_path)

from mbrole import functional_enrichment as fe


def test_enrichment():
    query = {"A","B", "C","D","E"}
    background = {"A","B","C","D","E","F","G","H","I"}
    category = {"B","C","D","E"}
    pval = fe.functional_enrichment(query, category, background)
    print(pval)