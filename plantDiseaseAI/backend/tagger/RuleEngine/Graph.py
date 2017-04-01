# -*- coding: utf-8 -*-
import re
from itertools import permutations
import copy
import os,sys
import pprint
from AST import *

pp = pprint.PrettyPrinter(indent = 2)

class Node(object):
    def __init__(self):
        self._edges = []
        self._rules = []
        self._postActions = []
        self._prevActions = []
        self._id = 0
    def endNode(self):
        if len(self._rules) > 0:
            return True
        else:
            return False

class Edge(object):
    def __init__(self, node):
        self._dest = node
        self._predicate = None
        self._actions = []

class EdgeAction(object):
    def __init__(self, astAction):
        self._toNodes = []
        self._fromNodes = []
        self._edges = []
        self._astAction = astAction
        self._seqId = -1
        self._actId = -1

class Graph(object):
    def __init__(self):
        self._nodes = []
        self._startNode = Node()
        self._edgeActions = []
        self._ruleMap = None
        self._actions = []
        self._actionSeqId = 0
        self._actionId = 0

    def addNode(self, node):
        node._id = len(self._nodes)
        self._nodes.append(node)

    def addEdge(self, start, end, pred, actions):
        edge = Edge(end)
        edge._predicate = pred
        edge._actions.extend(actions)
        start._edges.append(edge)

    def buildGraph(self, ast):
        self._nodes.append(self._startNode)
        # store rule maps
        self._ruleMap = ast._ruleMap
        # build sub-graph for each rule
        for ruleName in self._ruleMap.keys():
            rule = self._ruleMap[ruleName]
            start = Node()
            end = Node()
            self.addNode(start)
            self.addNode(end)
            actions = []
            self.buildSubGraph(start, end, rule._value, actions)
            end._rules.append(ruleName)
            self.addEdge(self._startNode, start, None, [])

    def isNode(self, expr):
        if isinstance(expr, UnaryOpNode):
            return True
        elif isinstance(expr, BinaryOpNode):
            return True
        elif isinstance(expr, AtomCover):
            return True
        elif isinstance(expr, Atom):
            return True
        elif isinstance(expr, TokenValue):
            return True
        elif isinstance(expr, Span):
            return True
        else:
            return False
        
    def buildSubGraph(self, start, end, expr, actions):
        # recuisively build expr from newStart to newEnd
        if self.isNode(expr):
            pred = self.buildPredicate(expr)
            self.addEdge(start, end, pred, actions)
            return
        # check the count and actions
        for act in expr._actions:
            edgeAct = EdgeAction(act)
            actions.append(edgeAct)
            self._actions.append(edgeAct)
            start._postActions.append(edgeAct)
            end._prevActions.append(edgeAct)
        newStart = start
        newEnd = end
        # check the count 
        if expr._count == '?':
            pass
        elif expr._count == '*':
            curNode = Node()
            self.addNode(curNode)
            self.addEdge(start, curNode, None, actions)
            self.addEdge(curNode, end, None, actions)
            newStart = curNode
            newEnd = curNode
        elif expr._count == '+':
            n1 = Node()
            n2 = Node()
            self.addNode(n1)
            self.addNode(n2)
            self.addEdge(start, n1, None, actions)
            self.addEdge(n2, n1, None, actions)
            self.addEdge(n2, end, None, actions)
            newStart = n1
            newEnd = n2
        if isinstance(expr, TermSeq):
            if expr._type == 'ordered':
                fromNode = newStart
                toNode = None
                num = len(expr._terms)
                for i in range(num):
                    if i == num - 1:
                        toNode = newEnd
                    else:
                        toNode = Node()
                        self.addNode(toNode)
                    self.buildSubGraph(fromNode, toNode, expr._terms[i], actions)
                    fromNode = toNode
            else:
                for term in expr._terms:
                    self.buildSubGraph(newStart, newEnd, term, actions)
        elif isinstance(expr, ExprTree):
            self.buildSubGraph(newStart, newEnd, expr._root, actions)
        else:
            raise TypeError('cannot handle type [' + str(type(expr)) + '] for building graph')

        if expr._count == '?':
            self.addEdge(start, end, None, actions)

        # handle actions (seqId, Id)
        actionNum = len(expr._actions)
        if actionNum == 0:
            return
        self._actionId = self._actionId + actionNum
        for i in range(actionNum):
            act = actions.pop()
            act._seqId = self._actionSeqId
            act._actId = self._actionId  - i - 1
        self._actionSeqId = self._actionSeqId + 1

    def buildPredicate(self, node):
        #print "XXXX:" + str(type(node))
        if isinstance(node, ExprTree):
            return self.buildPredicate(node._root)

        if isinstance(node, TokenValue):
            return TokenValuePredicate(node._value)
        elif isinstance(node, Atom):
            return AtomPredicate()
        elif isinstance(node, AtomCover):
            return AtomCoverPredicate()
        elif isinstance(node, Span):
            pred = SpanPredicate(node._type)
            if node._key != '':
                pred.addKV(node._key, node._value)
            return pred
        elif isinstance(node, UnaryOpNode):
            return NotPredicate(self.buildPredicate(node._node))
        elif isinstance(node, BinaryOpNode):
            if node._operation == '&&':
                return AndPredicate(self.buildPredicate(node._nodeLeft), \
                            self.buildPredicate(node._nodeRight))
            else:
                return OrPredicate(self.buildPredicate(node._nodeLeft), \
                    self.buildPredicate(node._nodeRight))
        else:
            raise TypeError('unknown Node for building Predicate: [' + str(type(node)) +']')

    def dumpPredicate(self, pred, fd):
        if isinstance(pred, TokenValuePredicate):
            fd.write(pred._val.strip('"').encode('utf-8'))
        elif isinstance(pred, AtomPredicate):
            fd.write("<atom>")
        elif isinstance(pred, AtomCoverPredicate):
            fd.write("<atomcover>")
        elif isinstance(pred, SpanPredicate):
            fd.write('<' + pred._type + '>')
        elif isinstance(pred, NotPredicate):
            fd.write('NOT(')
            self.dumpPredicate(pred._pred,fd)
            fd.write(')')
        elif isinstance(pred, AndPredicate):
            fd.write('AND(')
            self.dumpPredicate(pred._pred1,fd)
            self.dumpPredicate(pred._pred2,fd)
            fd.write(')')
        elif isinstance(pred, OrPredicate):
            fd.write('OR(')
            self.dumpPredicate(pred._pred1,fd)
            self.dumpPredicate(pred._pred2,fd)
            fd.write(')')
        else:
            raise TypeError('unknown predicate:' + str(type(pred)) + ' type for dumping')

    def dumpActions(self, action, fd):
        astAct = action._astAction
        if astAct._type == 'Slot':
            fd.write('slot:' + astAct._k)
        elif astAct._type == 'General':
            fd.write(astAct._k + '=' + astAct._v)
        else:
            raise TypeError("unknown action type")
    def dumpNodeEdge(self, start, edge, printActions, fd):
        fd.write('n' + str(start._id) + '->' + 'n' + str(edge._dest._id))
        fd.write(' [label="')
        if edge._predicate is None:
            fd.write('e')
        else:
            self.dumpPredicate(edge._predicate, fd)
        if printActions:
             for action in edge._actions:
                 fd.write('\\nact(' + str(action._actId) +',' + str(action._seqId) +') ')
                 self.dumpActions(action, fd)
        fd.write('"];\n')
    def dumpNode(self, node, printEdges, printActions, fd):
        if printEdges:
            for edge in node._edges:
                self.dumpNodeEdge(node, edge, printActions, fd)
        fd.write('n' + str(node._id) + ' [label="' + ';'.join(node._rules) + '"]\n')

    def dump(self, filename):
        indent = ' ' * 4
        with open(filename, 'w') as fd:
            fd.write('digraph ruleGraph {' + '\n')
            fd.write('rankdir=LR;' + '\n')
            nodeId = 0
            for node in self._nodes:
                self.dumpNode(node, True, True, fd)
            fd.write('}')

class Predicate(object):
    def __init__(self):
        pass

class TokenValuePredicate(Predicate):
    def __init__(self, tokVal):
        self._val = tokVal

class AtomPredicate(Predicate):
    def __init__(self):
        pass

class AtomCoverPredicate(Predicate):
    def __init__(self):
        pass

class SpanPredicate(Predicate):
    def __init__(self, spanType):
        self._type = spanType
        self._checks = {}
    # "v" is "" means, we only check the key existence
    def addKV(self, k, v):
        self._checks[k] = v

class NotPredicate(Predicate):
    def __init__(self, pred):
        self._pred = pred

class AndPredicate(Predicate):
    def __init__(self, pred1, pred2):
        self._pred1 = pred1
        self._pred2 = pred2

class OrPredicate(Predicate):
    def __init__(self, pred1, pred2):
        self._pred1 = pred1
        self._pred2 = pred2
