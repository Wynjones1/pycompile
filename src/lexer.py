#!/usr/bin/env python3
import re
from collections import namedtuple, OrderedDict
from enum import Enum

keywords = (
    "function",
    "if",
    "else",
    "elif",
    "while",
    "return",
    "decl"
)

class Associativity(Enum):
    LEFT  = 0
    RIGHT = 1

operations = {
    "*"  : (10, Associativity.LEFT),
    "/"  : (10, Associativity.LEFT),
    "%"  : (10, Associativity.LEFT),
    "+"  : (9,  Associativity.LEFT),
    "-"  : (9,  Associativity.LEFT),
    "<"  : (8,  Associativity.LEFT),
    "<=" : (8,  Associativity.LEFT),
    ">"  : (8,  Associativity.LEFT),
    ">=" : (8,  Associativity.LEFT),
    "==" : (7,  Associativity.LEFT),
    "!=" : (7,  Associativity.LEFT),
}

class TokenTypes(Enum):
    NONE        = 0
    INT_LITERAL = 1
    KEYWORD     = 2
    IDENTIFIER  = 3
    LPAREN      = 4
    RPAREN      = 5
    LBRACE      = 6
    RBRACE      = 7
    RARROW      = 8
    LARROW      = 9
    BINOP       = 10
    SEMICOLON   = 11
    WHITESPACE  = 12
    COLON       = 13
    ASSIGN      = 14
    EOF         = 15

token_regexprs = (
    (TokenTypes.INT_LITERAL, r"[0-9]+"),
    (TokenTypes.IDENTIFIER,  r"[a-zA-Z][a-zA-Z0-9_]*"),
    (TokenTypes.LARROW,      re.escape("->")),
    (TokenTypes.LARROW,      re.escape("<-")),
    (TokenTypes.ASSIGN,      re.escape(":=")),
    (TokenTypes.LPAREN,      re.escape("(")),
    (TokenTypes.RPAREN,      re.escape(")")),
    (TokenTypes.LBRACE,      re.escape("{")),
    (TokenTypes.RBRACE,      re.escape("}")),
    (TokenTypes.SEMICOLON,   re.escape(";")),
    (TokenTypes.COLON,       re.escape(",")),
    (TokenTypes.BINOP,       "|".join([re.escape(x) for x in operations])),
    (TokenTypes.WHITESPACE,  r"[ \t\n]"),
)

class Token(namedtuple("Token", ["type", "data", "line", "column"])):
    def underline(self, data):
        t = data.split("\n")[self.line - 1]
        a = self.column - 1
        b = len(self.data) - 1
        c = len(t) - a - b - 1
        t += "\n" + " " * a + "^" + "~" * b + " " * c
        return t

    def __repr__(self):
        return 'Token({},"{}")'.format(self.type.name, self.data)

    def __str__(self):
        return self.data

    def __eq__(self, other):
        if isinstance(other, str):
            return self.data == other
        elif isinstance(other, TokenTypes):
            return self.type == other
        return False

    def __ne__(self, other):
        return not (self == other)

class LexerException(Exception):
    pass

""" returns (toktext, type, rest) """
def get_next(data):
    toktext = ""
    toktype = None
    for type, regex in token_regexprs:
        match = re.match(r"^({})(.*)".format(regex), data, re.DOTALL)
        if match:
            tok_data = match.groups()[0]
            if len(tok_data) > len(toktext):
                toktext = tok_data
                toktype = type

    if toktype == None or toktext == "":
        raise LexerException()

    return toktext, toktype, data[len(toktext):]

def lex(data):
    line   = 1
    column = 1
    while data:
        tok, type, data = get_next(data)

        if type == TokenTypes.IDENTIFIER and tok in keywords:
            type = TokenTypes.KEYWORD
        if type != TokenTypes.WHITESPACE:
            yield Token(type, tok, line, column)
        column += len(tok)
        if tok == "\n":
            line += 1
            column = 1
    yield Token(TokenTypes.EOF, "", line, column)