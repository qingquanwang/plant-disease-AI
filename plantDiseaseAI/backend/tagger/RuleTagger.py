# -*- coding: utf-8 -*-
from ruleEngine import *
import pprint

pp = pprint.prettyprinter(indent = 2)

def TraverseContext(object):
    def __init__(self, spanGraph, endPos):
        self._path = []
        self._continued = False
        self._matched = False
        self._inputGraph = spanGraph
        self._endPos = endPos
        self._deadStates = {}
        self._hitSequence = []

def ruleTagger(Tagger):
    def __init__(self):
        pass
    def loadRules(self, ruleFile):
        pass
    def walk(self, pos, node, ctx):
        ctx._matched = False
        # check dead states
        state_sig = str(node._id) + '-' + str(pos)
        if state_sig in self._deadStates:
            return
        # match a final state
        if (node.endNode() == True) and (pos == ctx._endPos):
            ctx._matched = True
            # execute actions
        else:
            matched = False
            for edge in node._edges:
                if ctx._continued == False:
                    break
                if edge._predicate == None:
                    ctx._path.append((None, edge))
                    self.walk(pos, edge._dest, ctx)
                    ctx._matched = (ctx._matched or matched)
                    ctx.path.pop()
                else:
                    # Find the overlap of edges
                    while(
    def tag(self, spanGraph, seqList):
        
        pass
