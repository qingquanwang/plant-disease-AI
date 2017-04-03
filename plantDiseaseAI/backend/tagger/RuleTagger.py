# -*- coding: utf-8 -*-
from ruleEngine import *
from Tagger import *
import pprint

pp = pprint.prettyprinter(indent = 2)

class TraverseContext(object):
    def __init__(self, spanGraph):
        self._path = []
        self._continued = False
        self._matched = False
        self._inputGraph = spanGraph
        self._deadStates = {}
        self._hitSequence = []

    def isEnd(self, pos):
        if pos in self._inputGraph._startMap:
            return True
        else:
            return False

class ruleTagger(Tagger):
    def __init__(self):
        self._graph = None

    def loadRules(self, ruleFile):
        with open(filename, 'r') as fd:
            data = fd.read().decode('utf-8')
            lexer = lex.lex(debug=1, optimize=0,
                                lextab='lextab', reflags=0)
            lexer.input(data)
            '''
            for tok in iter(lexer.token, None):
                if not tok:
                    break
                sys.stdout.write('(%s,%s,%d,%d)\n' % (tok.type, tok.value.encode('utf-8'), tok.lineno, tok.lexpos))
            '''
        
            parser = yacc.yacc()
            result = parser.parse(lexer=lexer)
            ast = AST(result)
            ast.expand()
        
            self._graph = Graph()
            self._graph.buildGraph(ast)

    def execute_actions(self, ctx, seq):
        for (spanId, edge) in ctx._path:
            for act in edge._actions:
                if act._astAction._type == 'Slot':
                    if 'slots' in seq._annotation:
                        if act._astAction._k in  seq._annotation['slots']:
                            seq._annotation['slots'][act._astAction._k].append(spanId)
                        else:
                            seq._annotation['slots'][act._astAction._k] = [spanId]
                    else:
                        seq._annotation['slots'] = {}
                        seq._annotation['slots'][act._astAction._k] = [spanId]
                else act._astAction._type == 'General':
                    seq._annotation[act._astAction._k] = act._astAction._v

    def walk(self, pos, node, ctx):
        ctx._matched = False
        # check dead states
        state_sig = str(node._id) + '-' + str(pos)
        if state_sig in self._deadStates:
            return
        # match a final state
        if (node.endNode() == True) and ctx.isEnd(pos):
            ctx._matched = True
            # generate sequence
            seq = Sequence()
            seq._source = 'RuleTagger'
            seq._prob = '0.9' #hardcode
            for (spanId, edge) in ctx._path:
                seq._spans.append(spanId)
            self._hitSequence.append(seq)
            # execute actions
            self.execute_actions(ctx, seq)
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
                    spanEdges = ctx._inputGraph._startMap[pos]
                    for spanId in spanEdges:
                        inputSpan = ctx._inputGraph._spans[spanId]
                        if self.matchEdge(inputSpan, edge._predicate):
                            ctx._path.append((spanId, edge))
                            self.walk(pos + inputSpan._len, edge._dest, ctx)
                            ctx._matched = (ctx._matched or matched)
                            ctx.path.pop()
                            if isinstance(edge._predicate, AtomPredicate):
                                break
            ctx._matched = matched
            if matched == False:
                self._deadStates[str(node._id) + '-' + str(pos)] = 1

    def matchEdge(self, span, pred):
        if isinstance(pred, AtomPredicate):
            return (span._type == 'tok')
        elif isinstance(pred, SpanPredicate):
            if span._type == pred._type:
                for (k,v) in pred._checks.items():
                    if v == '':
                        if k in span._attrs:
                            return True
                        else:
                            return False
                    else:
                        if k in span._attrs:
                            return (span._attrs[k] == v)
                        else:
                            return False
            else:
                return False
        elif isinstance(pred, TokenValuePredicate):
            if span._type != 'tok':
                return False
            else:
                return (span._text == pred.val)
        elif isinstance(pred, NotPredicate):
            return self.matchEdge(span, pred._pred)
        elif isinstance(pred, AndPredicate):
            return (self.matchEdge(span, pred._pred1) and self.matchEdge(span, pred._pred2))
        elif isinstance(pred, OrPredicate):
            return (self.matchEdge(span, pred._pred1) or self.matchEdge(span, pred._pred2))
        else:
            raise TypeError('Unknown predicate type for matching edge: [' + \
                                str(type(pred)) + ']')

    def tag(self, spanGraph, seqList):
        ctx = TraverseContext()
        self.walk(0, self._graph._startNode)
        for s in self._hitSequence:
            seqList.append(s)
