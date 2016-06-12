#!/usr/bin/env python3
from . import lexer
from . import ast
import contextlib
import functools

class ParseError(Exception):
    pass

class ParseFail(Exception):
    pass

class TokenState(object):
    def __init__(self, data):
        self.tokens = [x for x in lexer.lex(data)]
        self.pos = 0

    def __getitem__(self, index):
        try:
            return self.tokens[self.pos + index]
        except IndexError:
            raise ParseFail()

    def peek(self):
        return self[0]

    def next(self):
        out = self.peek()
        self.pos += 1
        return out

    
def accept(tokens, value):
    if tokens.peek() == value:
        return tokens.next()
    return None

def expect(tokens, value):
    out = accept(tokens, value)
    if out is not None:
        return out
    raise ParseFail()

@contextlib.contextmanager
def parenthesis(tokens):
    if not accept(tokens, "("):
        raise ParseFail()
    yield
    expect(tokens, ")")

@contextlib.contextmanager
def braces(tokens):
    if not accept(tokens, "{"):
        raise ParseFail()
    yield
    expect(tokens, "}")

@contextlib.contextmanager
def error_on_fail(msg):
    try:
        yield
    except ParseFail:
        raise ParseError(msg)

def parse_any(tokens, *funcs):
    for f in funcs:
        with contextlib.suppress(ParseFail):
            return f(tokens)
    raise ParseFail()

depth = 0
def parsefunc(function):
    @functools.wraps(function)
    def out(tokens, *args, **kwargs):
        global depth
        pos = tokens.pos
        depth += 1
        try:
            out = function(tokens, *args, **kwargs)
            depth -= 1
            return out
        except:
            tokens.pos = pos
            depth -= 1
            raise
    return out

@parsefunc
def identifier(tokens):
    return ast.Identifier(str(expect(tokens, lexer.TokenTypes.IDENTIFIER)))

@parsefunc
def literal(tokens):
    return ast.IntegerLiteral(str(expect(tokens, lexer.TokenTypes.INT_LITERAL)))

@parsefunc
def op(tokens):
    return ast.Operation(str(expect(tokens, lexer.TokenTypes.BINOP)))

@parsefunc
def type_(tokens):
    if accept(tokens, "int"):
        return ast.Type("int")
    raise ParseFail()

@parsefunc
def function_params(tokens):
    out = ast.FunctionParams()
    while True:
        with contextlib.suppress(ParseFail):
            temp = ast.Param()
            temp.type = type_(tokens)
            temp.id   = identifier(tokens)
            out.append(temp)
        if not accept(tokens, ","):
            break
    return out

@parsefunc
def return_(tokens):
    expect(tokens, "return")
    with error_on_fail("Could not parse return statement"):
        out = ast.Return()
        with contextlib.suppress(ParseFail):
            out.expr = expression(tokens)
        return out


@parsefunc
def expression_list(tokens):
    out = ast.ExpressionList()
    while True:
        with contextlib.suppress(ParseFail):
            out.append(expression(tokens))
        if not accept(tokens, ","):
            break
    return out

@parsefunc
def func_call(tokens):
    out = ast.FuncCall()
    out.id = identifier(tokens)
    with parenthesis(tokens):
        out.exprs = expression_list(tokens)
    return out

@parsefunc
def term(tokens):
    return parse_any(tokens, func_call, identifier, literal)

@parsefunc
def expression(tokens):
    queue = []
    stack = []

    with contextlib.suppress(ParseFail):
        while True:
            queue.append(term(tokens))
            o1 = op(tokens)
            o1_prec, o1_assoc = lexer.operations[o1.value]
            while len(stack):
                o2_prec, o2_assoc = lexer.operations[stack[-1].value]
                if (o1_assoc == lexer.Associativity.LEFT and o1_prec <= o2_prec) or o1_prec < o2_prec:
                    queue.append(stack.pop())
                else:
                    break
            stack.append(o1)

    queue += stack[::-1]
    stack = []

    try:
        stack.append(queue.pop(0))
        stack.append(queue.pop(0))
        while len(queue) or len(stack) > 1:
            if isinstance(queue[0], ast.Operation):
                binop = ast.Binop(lhs=stack.pop(-2), rhs=stack.pop(-1), op=queue.pop(0))
                stack.append(binop)
            else:
                stack.append(queue.pop(0))
    except IndexError:
        if len(stack) == 1 and not isinstance(stack[0], ast.Operation):
            return stack.pop()
        raise ParseFail()
    return stack.pop()

@parsefunc
def assign(tokens):
    id = identifier(tokens)
    expect(tokens, ":=")
    expr = expression(tokens)
    return ast.Assign(id, expr)

@parsefunc
def decl(tokens):
    expect(tokens, "decl")
    with error_on_fail("Error parsing decl"):
        out = ast.Declare()
        with parenthesis(tokens):
            out.type_ = type_(tokens)
        out.id = identifier(tokens)
        expect(tokens, ":=");
        out.initial_value = expression(tokens)
        return out

@parsefunc
def else_(tokens):
    expect(tokens, "else")
    return braced_stmt_list(tokens)

@parsefunc
def elif_(tokens):
    expect(tokens, "elif")
    out = ast.If()
    with parenthesis(tokens):
        out.cond = expression(tokens)
    out.true_branch = braced_stmt_list(tokens)
    with contextlib.suppress(ParseFail):
        out.false_branch = parse_any(tokens, else_, elif_)
    return out

@parsefunc
def braced_stmt_list(tokens):
    with braces(tokens):
        return statement_list(tokens)

@parsefunc
def if_(tokens):
    expect(tokens, "if")
    with error_on_fail("Could not parse if"):
        out = ast.If()
        with parenthesis(tokens):
            out.cond = expression(tokens)
        out.true_branch = braced_stmt_list(tokens)
        with contextlib.suppress(ParseFail):
            out.false_branch = parse_any(tokens, else_, elif_)
        return out

@parsefunc
def while_(tokens):
    expect(tokens, "while")
    with error_on_fail("Could not parse while"):
        out = ast.While()
        with parenthesis(tokens):
            out.cond = expression(tokens)
        out.statements = braced_stmt_list(tokens)
        return out

@parsefunc
def statement(tokens):
    # statements that end in ";"
    with contextlib.suppress(ParseFail):
        out = parse_any(tokens, decl, return_, assign, expression)
        expect(tokens, ";")
        return out
    # statements that don't end in ";"
    return parse_any(tokens, if_, while_)

@parsefunc
def statement_list(tokens):
    out = ast.StatementList()
    while True:
        try:
            out.append(statement(tokens))
        except ParseFail:
            break
    return out

@parsefunc
def function(tokens):
    expect(tokens, "function")
    with error_on_fail("Could not parse function"):
        out = ast.Function()
        out.id = identifier(tokens)
        with parenthesis(tokens):
            out.params = function_params(tokens)
        if accept(tokens, "->"):
            out.return_type = type_(tokens)
        out.statements = braced_stmt_list(tokens)
        return out

@parsefunc
def function_list(tokens):
    out = ast.FunctionList()
    while True:
        try:
            out.append(function(tokens))
        except ParseFail:
            break
    return out

def parse(data, f = function_list):
    tokens = TokenState(data)
    out = f(tokens)
    if not accept(tokens, lexer.TokenTypes.EOF):
        raise ParseFail("Unexpected input.")
    return out