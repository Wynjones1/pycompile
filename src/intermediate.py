#!/usr/bin/env python3
from collections import defaultdict
from . import ast

class TransformState(object):
    def __init__(self):
        self.temp_count = -1
        self.label_count = -1
        self.id_mapping = defaultdict(lambda : -1)

    def next(self, value):
        return self.id_mapping[value] + 1

    def temp(self):
        self.temp_count += 1
        self._last_temp = ast.Identifier("_t{}".format(self.temp_count))
        return self._last_temp

    def label(self):
        self.label_count += 1
        return Label(self.label_count)

    def set_last(self, var):
        self._last_temp = var

    def last_temp(self):
        return self._last_temp

class IntermediateRep(object):
    def __init__(self):
        self.next = None
        self.prev = None

    def __str__(self, **kwargs):
        raise NotImplementedError("For {}".format(self.__class__.__name__))


class BasicBlock(object):
    def __init__(self):
        self.first = None
        self.last  = None

    def append(self, node):
        if self.first == None:
            self.first = node
            self.last = node
        else:
            self.last.next = node
            self.last = node

    def join(self, bb):
        pass

class InstructionList(list):
    def __init__(self):
        pass

    def __iadd__(self, obj):
        try:
            return super().__iadd__(obj)
        except:
            self.append(obj)
            return self

class Program(IntermediateRep):
    pass

class ParamList(list, IntermediateRep):
    def __init__(self):
        return super().__init__()

class Function(IntermediateRep):
    def __init__(self, id=None, params=None, return_type=None):
        self.id = id
        self.params = params
        self.return_type = return_type
        self.instructions = InstructionList()

    def __str__(self, **kwargs):
        return "function {}".format(self.id)

class Label(IntermediateRep):
    def __init__(self, idx):
        self.idx = idx
        self.references = []

    def __str__(self):
        return "L{}:".format(self.idx)

class Jmp(IntermediateRep):
    def __init__(self, label):
        self.label = label
        label.references.append(self)

    def __str__(self):
        return "Jmp {}".format(self.label)

class JmpIf(IntermediateRep):
    def __init__(self, label, var):
        self.label = label
        self.var   = var
        label.references.append(self)

class JmpNotIf(IntermediateRep):
    def __init__(self, label, var):
        self.label = label
        self.var = var
        label.references.append(self)

    def __str__(self):
        return "Jmp !{} {}".format(self.var, self.label)

class Op(IntermediateRep):
    def __init__(self, result, op, lhs, rhs):
        self.op = op
        self.lhs = lhs
        self.rhs = rhs
        self.result = result

    def __str__(self):
        return "{} <- {} {} {}".format(self.result, self.lhs, self.op, self.rhs)

class Assign(IntermediateRep):
    def __init__(self, dest, src):
        self.dest = dest
        self.src  = src

    def __str__(self):
        return "{} <- {}".format(self.dest, self.src)

class Call(IntermediateRep):
    def __init__(self, id, result):
        self.id = id
        self.result = result

    def __str__(self):
        return "{} <- call {}".format(self.id, self.result)

class Return(IntermediateRep):
    def __init__(self, var):
        self.var = var

    def __str__(self):
        return "return {}".format(self.var if self.var else "")

class FunctionList(IntermediateRep, list):
    pass