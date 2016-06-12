import unittest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src import parser
from src import ast

class Test_symbol_table(unittest.TestCase):
    def test_new_scope(self):
        table = ast.SymbolTable()
        scope = table.new_scope()
        table["a"] = 10
        scope["a"] = 10

    def test_multiple_inserts(self):
        table = ast.SymbolTable()
        table["a"] = 10
        table["a"] = 10

if __name__ == '__main__':
    unittest.main()
