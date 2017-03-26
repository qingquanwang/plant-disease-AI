import os,sys

class Rule(object):
    def __init__(self, ruleType, name, value):
        self._type = ruleType
        self._name = name
        self._value = value

class Action(object):
    def __init__(self, annType, key, value):
        if annType in ['Slot', 'General']:
            self._type = annType
        else:
            raise TypeError("unknown action type")
        self._k = key
        self._v = value


class Term(object):
    def __init__(self, count, actions):
        self._actions = []
        self._count = '\0'
        self._actions = []
        if count in ['\0', '?', '+', '*']:
            self._count = count
        else:
            raise TypeError("unknow count indicator")
        if actions == None:
            return
        for act in actions:
            self._actions.append(act)

class TermSeq(Term):
    def __init__(self, seqType, termList):
        super(TermSeq, self).__init__('\0', None)
        self._type = "ordered"
        self._terms = []
        if seqType in ["ordered", "unordered", "mirror", "altered"]:
            self._type = seqType
        else:
            raise TypeError("unknown seq type")
        for term in termList:
            self._terms.append(term)
    def setCounted(self, count, actions):
        if count in ['\0', '?', '+', '*']:
            self._count = count
        else:
            raise TypeError("unknown count indicator")
        for act in actions:
            self._actions.append(act)

class Call(Term):
    def __init__(self, name, value):
        super(Call, self).__init__('\0', None)
        self._name = name
        self._value = value

class ExprTree(Term):
    def __init__(self, root):
        super(ExprTree, self).__init__('\0', None)
        self._root = root

class Node(object):
    def __init__(self):
        pass

class UnaryOpNode(Node):
    def __init__(self, operation, node):
        self._node = node
        if operation in ['!']:
            self._operation = operation
        else:
            raise TypeError("unknown unary operation")

class BinaryOpNode(Node):
    def __init__(self, operation, node1, node2):
        if operation in ['&&', '||']:
            self._operation = operation
        else:
            raise TypeError("unknown binary operation")
        self._nodeLeft = node1
        self._nodeRight = node2

class AtomCover(object):
    def __init__(self):
        pass

class Atom(Node):
    def __init__(self):
        pass

class TokenValue(Node):
    def __init__(self, value):
        self._value = value

class TokenValueDict(Node):
    def __init__(self, values):
        for v in values:
            self._values.append(v)

class Span(Node):
    def __init__(self, spanType, key, value):
        self._type = spanType
        self._key = key
        self._value = value

class AST(object):
    def __init__(self, rules):
        self._rules = rules
    def dumpAST(self):
        for rule in self._rules:
            print (rule._name + ':' + '[' + rule._value + ']').encode('utf-8')

class ParseContext(object):
    def __init__(self):
        self._hasErrors = False
