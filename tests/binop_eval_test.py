import unittest
import sys
import os
import random
from contextlib import suppress
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import parser
from src import ast
from src import lexer

def eval_expr(result : ast.Binop):
    x = result.print()

class ParserTestCase(unittest.TestCase):
    def assertEvalsTo(self, data, result):
        def eval_expr(data):
            try:
                lhs = eval_expr(data.lhs)
                rhs = eval_expr(data.rhs)
                return "({} {} {})".format(lhs, data.op.value, rhs)
            except:
                return data.value

        ast = parser.parse(data, parser.expression)
        value = eval_expr(ast).replace("/", "//")
        evaled = str(eval(value))
        self.assertEqual(evaled, result)

def random_expression(operations = list(lexer.operations.keys()), length = 100, min = 0, max=10):
    while True:
        try:
            out = str(random.randint(min, max))
            for i in range(length - 1):
                out += " {} {}".format(random.choice(operations), random.randint(min, max))
            return out, str(eval(out.replace("/", "//")))
        except ZeroDivisionError:
            pass

class Test_binop_eval_test(ParserTestCase):
    def test_0(self):
        self.assertEvalsTo("1 + 1", "2")
    
    def test_1(self):
        self.assertEvalsTo("1 + 2", "3")

    def test_2(self):
        self.assertEvalsTo("2 * 2", "4")

    def test_3(self):
         self.assertEvalsTo("1 + 2 - 3 * 4", "-9")

    def test_random_expression_0(self):
        expr, result = random_expression(operations = ["+", "-", "*", "/"])
        self.assertEvalsTo(expr, result)

    def test_random_expression_1(self):
        expr, result = random_expression(operations = ["+", "-", "*", "/", "%"])
        self.assertEvalsTo(expr, result)

    def test_random_short_expressions_0(self):
        for x in range(100):
            expr, result = random_expression(operations = ["+", "-", "*", "/", "%"], length = 10)
            self.assertEvalsTo(expr, result)

    def test_random_short_expressions_0(self):
        for x in range(10):
            expr, result = random_expression(operations = ["+", "-", "*", "/", "%"], length = 100)
            self.assertEvalsTo(expr, result)


if __name__ == '__main__':
    unittest.main()
