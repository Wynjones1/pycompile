#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import os
from glob import glob
from src import parser

def printf(strformat, *args, **kwargs):
    print(strformat.format(*args, **kwargs))

def run_test(testfile):
    with open(testfile, "r") as fp:
        data = fp.read()
    function_name, *tests = [x.strip() for x in data.split("===\n")]
    printf("Running fragment test for function '{}'\n{}", function_name, "=" * 60)
    func = getattr(parser, function_name)
    for test in tests:
        ast = parser.parse(test, func)
        print(ast)
    print("")

def main(argv):
    test_path = os.path.join(os.path.dirname(__file__), "fragments")
    if 1:
        tests = glob(os.path.join(test_path, "*.txt"))
    else:
        tests = [os.path.join(test_path, "test.txt")]
    for test in tests:
        run_test(test)

if __name__ == "__main__":
    main(sys.argv[1:])