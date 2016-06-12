#!/usr/bin/env python3
from collections import namedtuple
from .           import intermediate
from contextlib  import contextmanager
import functools

def semanticsfunc(func):
    @functools.wraps(func)
    def out(self, table = SymbolTable()):
        self.symbol_table = table
        out = func(self, table)
        return out
    return out

class SemanticsException(Exception):
    pass

class SymbolTable(dict):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

    def __setitem__(self, key, value):
        if key in self:
            raise SemanticsException("Trying to insert existing identifier '{}' into scope.".format(key))
        return super().__setitem__(str(key), value)

    def __getitem__(self, y):
        try:
            return super().__getitem__(str(y))
        except KeyError as e:
            if self.parent is not None:
                return self.parent[str(y)]
            raise SemanticsException("Cannot find variable '{}'".format(y)) from e

    def new_scope(self):
        return SymbolTable(self)

class AST(object):
    def to_intermediate(self, state):
        raise NotImplementedError("For {}".format(self.__class__.__name__))

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        raise NotImplementedError("For {}".format(self.__class__.__name__))

class Param(AST):
    def __init__(self):
        self.type = None
        self.id   = None

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        type_ = self.type.check_semantics(table)
        table[self.id] = type_
        return type_

class Return(AST):
    def __init__(self, expr=None):
        self.expr = None

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        if self.expr is None:
            if table["_return"] is not None:
                raise SemanticsException("return must be of type {}".format(table["_return"]))
            return None
        if table["_return"] is None:
            raise SemanticsException("Cannot return value from void function")
        expr_type = self.expr.check_semantics(table)
        if not expr_type.convertable_to(table["_return"]):
            raise SemanticsException("Cannot convert type '{}' to '{}'".format(expr_type, table["_function"]))
        return table["_return"]

    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        var = None
        if self.expr is not None:
            out += self.expr.to_intermediate(state)
            var = state.last_temp()
        out += intermediate.Return(var)
        return out

class ValueType(AST):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "{}({})".format(type(self).__name__, self.value)

    def __str__(self):
        return str(self.value)

class Type(ValueType):
    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        if self.value == "int":
            return self
        raise SemanticsException("Type {} is not known".format(self.value))

    def convertable_to(self, other):
        return self.value == other.value

    def supports_operation_with(self, operation, other):
        return True

    def get_result_type(self, operation, other):
        if self.supports_operation_with(operation, other):
            return self
        raise SemanticsException("Type {} does not support '{}' operation with {}".format(self, operation, other))

class Identifier(ValueType):
    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        return table[self.value]

    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        #out += intermediate.Assign(state.temp(), self)
        state.set_last(self)
        return out

class IntegerLiteral(ValueType):
    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        return Type("int")

    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        #out += intermediate.Assign(state.temp(), self)
        state.set_last(self)
        return out

class Operation(ValueType):
    pass

class FuncCall(AST):
    def __init__(self, id=None, exprs=None):
        self.id = id
        self.exprs = exprs

class Binop(AST):
    def __init__(self, *, lhs = None, rhs = None, op = None):
        self.lhs = lhs
        self.rhs = rhs
        self.op  = op

    def __repr__(self):
        return "Binop{}".format(self.print())

    def print(self, depth=0):
        if isinstance(self.lhs, Binop):
            sl = self.lhs.print()
        else:
            sl = str(self.lhs)

        if isinstance(self.rhs, Binop):
            sr = self.rhs.print()
        else:
            sr = str(self.rhs)
        return "({} {} {})".format(sl, self.op, sr)

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        lhs_type = self.lhs.check_semantics(table)
        rhs_type = self.rhs.check_semantics(table)
        return lhs_type.get_result_type(self.op, rhs_type)

    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        out += self.lhs.to_intermediate(state)
        t0 = state.last_temp()
        out += self.rhs.to_intermediate(state)
        t1 = state.last_temp()
        out += intermediate.Op(state.temp(), self.op, t0, t1)
        return out

class Function(AST):
    def __init__(self, *, id=None, params=None, return_type=None, statements=None):
        self.id = id
        self.params = params
        self.return_type = return_type
        self.statements = statements

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        table[self.id] = self
        scope = table.new_scope()
        self.params.check_semantics(scope)
        # Store the return type in a dummy variable
        if self.return_type:
            scope["_return"] = self.return_type.check_semantics(scope)
        else:
            scope["_return"] = None
        self.statements.check_semantics(scope)

    def to_intermediate(self, state):
        out = intermediate.Function(self.id)
        for stmt in self.statements:
            out.instructions += stmt.to_intermediate(state)
        return out

class Assign(AST):
    def __init__(self, lhs=None, rhs=None):
        self.lhs = lhs
        self.rhs = rhs

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        lhs_type = self.lhs.check_semantics(table)
        rhs_type = self.rhs.check_semantics(table)
        if rhs_type.convertable_to(lhs_type):
            return lhs_type
        raise SemanticsException("Cannot assign type '{}' to type '{}'".format(rhs_type, lhs_type))

    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        out += self.rhs.to_intermediate(state)
        out += intermediate.Assign(self.lhs, state.last_temp())
        return out

class Declare(AST):
    def __init__(self, type_=None, id=None, initial_value=None):
        self.type_ = type_
        self.id    = id
        self.initial_value = initial_value

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        init_type = self.initial_value.check_semantics(table)
        decl_type = self.type_.check_semantics(table)
        if init_type.convertable_to(decl_type):
            table[self.id] = decl_type

    def to_intermediate(self, state):
        out = self.initial_value.to_intermediate(state)
        out += intermediate.Assign(self.id, state.last_temp())
        return out

class If(AST):
    def __init__(self, cond=None, true_branch=None, false_branch=None):
        self.cond = cond
        self.true_branch = true_branch
        self.false_branch = false_branch

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        cond_type = self.cond.check_semantics(table)
        self.true_branch.check_semantics(table.new_scope())
        if self.false_branch is not None:
            self.false_branch.check_semantics(table.new_scope())

    def to_intermediate(self, state):
        l0 = state.label()
        l1 = state.label()
        out =  self.cond.to_intermediate(state)
        out += intermediate.JmpNotIf(l0, state.last_temp())
        out += self.true_branch.to_intermediate(state)
        out += intermediate.Jmp(l1)
        out += l0
        if self.false_branch is not None:
            out += self.false_branch.to_intermediate(state)
        out += l1
        return out
        

class While(AST):
    def __init__(self, cond=None, statements=None):
        self.cond = cond
        self.statements = statements

    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        cond_type = self.cond.check_semantics(table)
        self.statements.check_semantics(table.new_scope())

    def to_intermediate(self, state):
        l0 = state.label()
        l1 = state.label()
        out = intermediate.InstructionList()
        out += l0
        out += self.cond.to_intermediate(state)
        out += intermediate.JmpNotIf(l1, state.last_temp())
        out += self.statements.to_intermediate(state)
        out += intermediate.Jmp(l0)
        out += l1
        return out

class ASTList(AST, list):
    @semanticsfunc
    def check_semantics(self, table = SymbolTable()):
        for x in self:
            x.check_semantics(table)

class FunctionList(ASTList):
    def to_intermediate(self, state):
        out = intermediate.FunctionList()
        for x in self:
            out.append(x.to_intermediate(state))
        return out

class StatementList(ASTList):
    def to_intermediate(self, state):
        out = intermediate.InstructionList()
        for stmt in self:
            out += stmt.to_intermediate(state)
        return out

class ExpressionList(ASTList):
    pass

class FunctionParams(ASTList):
    pass