import os,sys
import pprint

pp = pprint.PrettyPrinter(indent = 2)
indentInc = 2

class Rule(object):
    def __init__(self, ruleType, name, value):
        self._type = ruleType
        self._name = name
        self._value = value
    def dump(self, indent):
        if self._type == 'internal':
            out = ' ' * indent + 'InternalRule:[' + self._name +']'
        else:
            out = ' ' * indent + 'Rule:[' + self._name +']'
        print out
        self._value.dump(indent + indentInc)

class Action(object):
    def __init__(self, annType, key, value):
        if annType in ['Slot', 'General']:
            self._type = annType
        else:
            raise TypeError("unknown action type")
        self._k = key
        self._v = value
    def dump(self, indent):
        out = ' '*indent + 'Action: [' + self._type
        if self._type == 'General':
            out = out + ',' + self._k.encode('utf-8') + ',' + self._v.encode('utf-8') + ']'
        elif self._type == 'Slot':
            out = out + ',' + self._k.encode('utf-8') + ',' + 'AtomCover' + ']'
        else:
            out = out + ',' + self._k.encode('utf-8') + ',' + 'Unknown' + ']'
        print out

class Term(object):
    def __init__(self, count, actions):
        self._count = '\0'
        self._actions = []
        if count in ['\0', '?', '+', '*']:
            self._count = count
        else:
            raise TypeError("unknown count indicator")
        if actions == None:
            return
        for act in actions:
            self._actions.append(act)
    def translate_count(self):
        if self._count == '\0':
            return 'One'
        elif self._count == '\?':
            return 'OneOrZero'
        elif self._count == '\+':
            return 'OneOrMulti'
        else:
            return 'ZeroOrMulti'
    def dump(self, indent):
        out = ' ' * indent + 'Term:[count=' + self.translate_count() +']'
        print out
        for act in self._actions:
            act.dump(indent + indentInc)

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
    def dump(self, indent):
        out = ' ' * indent + 'TermSeq:[count=' + self.translate_count() 
        out = out + ',type=' + self._type + ']'
        print out
        for t in self._terms:
            t.dump(indent + indentInc)
        for act in self._actions:
            act.dump(indent + indentInc)

class Call(Term):
    def __init__(self, name, value):
        super(Call, self).__init__('\0', None)
        self._name = name
        self._value = value
    def dump(self, indent):
        print ' ' * indent + 'Call:[' + self._name +']'

class ExprTree(Term):
    def __init__(self, root):
        super(ExprTree, self).__init__('\0', None)
        self._root = root
    def dump(self, indent):
        #super(ExprTree,self).dump(indent)
        #print "Debug: " + str(type(self._root))
        self._root.dump(indent)

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
    def dump(self, indent):
        print ' ' * indent + 'NOT'
        self._node.dump(indent + indentInc)

class BinaryOpNode(Node):
    def __init__(self, operation, node1, node2):
        if operation in ['&&', '||']:
            self._operation = operation
        else:
            raise TypeError("unknown binary operation")
        self._nodeLeft = node1
        self._nodeRight = node2
    def dump(self, indent):
        out = ' ' * indent
        if self._operation == '&&':
            out = out + 'AND'
        else:
            out = out + 'OR'
        self._nodeLeft.dump(indent + indentInc)
        self._nodeRight.dump(indent + indentInc)

class AtomCover(object):
    def __init__(self):
        pass
    def dump(self, indent):
        print ' ' * indent + 'AtomCover'

class Atom(Node):
    def __init__(self):
        pass
    def dump(self, indent):
        print ' ' * indent + 'Atom'

class TokenValue(Node):
    def __init__(self, value):
        self._value = value
    def dump(self, indent):
        print ' ' * indent + 'TokenValue: [' + self._value.encode('utf-8') +']'

class TokenValueDict(Node):
    def __init__(self, values):
        for v in values:
            self._values.append(v)

class Span(Node):
    def __init__(self, spanType, key, value):
        self._type = spanType
        self._key = key
        self._value = value
    def dump(self, indent):
        out = ' ' * indent + 'Span: [' + self._type + ','
        out = out + self._key.encode('utf-8') + ',' 
        out = out + self._value.encode('utf-8') + ']'
        print out
"""
AST class graph:

rule := Rule(expr)
expr := counted := term := ExprTree(TermSeq)
TermSeq := expr[]

So usually the dump graph should be:
rule
    TermSeq
        TermSeq1
            Span
        TermSeq2
"""
class AST(object):
    def __init__(self, rules):
        self._rules = []
        self._rules.extend(rules)
    def dumpAST(self):
        for rule in self._rules:
            rule.dump(0)

class ParseContext(object):
    def __init__(self):
        self._hasErrors = False
