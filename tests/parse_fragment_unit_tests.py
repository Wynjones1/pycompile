import unittest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src import parser
from src import ast

class ParserTestCase(unittest.TestCase):
    def assertParsesTo(self, func, data, type_):
        self.assertIsInstance(parser.parse(data, func), type_)

class Test_parse_fragment_unit_tests(ParserTestCase):
    def test_while_0(self):
        self.assertParsesTo(parser.while_, "while(x < 10){x := x + 1;}", ast.While)

    def test_if_0(self):
        self.assertParsesTo(parser.if_, "if(a){return a;}", ast.If)

    def test_decl_0(self):
        self.assertParsesTo(parser.decl, "decl(int) x := 10", ast.Declare)

    def test_braced_stmt_list_0(self):
        self.assertParsesTo(parser.braced_stmt_list, "{}", list)

    def test_function_0(self):
        self.assertParsesTo(parser.function, "function a(){}", ast.Function)

    def test_function_1(self):
        self.assertParsesTo(parser.function, "function a() -> int {}", ast.Function)

    def test_function_2(self):
        self.assertParsesTo(parser.function, "function a(int x) -> int {}", ast.Function)

    def test_function_3(self):
        self.assertParsesTo(parser.function, "function a(int x, int y) -> int {}", ast.Function)

    def test_func_call_0(self):
        self.assertParsesTo(parser.func_call, "call()", ast.FuncCall)

    def test_func_call_1(self):
        self.assertParsesTo(parser.func_call, "call(other())", ast.FuncCall)

    def test_func_call_2(self):
        self.assertParsesTo(parser.func_call, "call(1,2,3)", ast.FuncCall)

    def test_expression_0(self):
        self.assertParsesTo(parser.expression, "1 + 2", ast.Binop)

    def test_expression_1(self):
        self.assertParsesTo(parser.expression, "1 + 2 - 3 * 4 / 5 % 6", ast.Binop)

    def test_if_0(self):
        self.assertParsesTo(parser.if_, "if(x){}else{}", ast.If)

    def test_if_1(self):
        self.assertParsesTo(parser.if_, "if(x){}elif(x){}else{}", ast.If)

if __name__ == '__main__':
    unittest.main()
