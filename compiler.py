#!/usr/bin/env python3
import sys
import argparse
from src import *

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default=None)
    parser.add_argument("inputs", nargs="+")
    args = parser.parse_args(argv)

if __name__ == "__main__":
    main(sys.argv[1:])