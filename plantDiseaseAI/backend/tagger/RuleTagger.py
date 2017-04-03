# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.tagger.RuleEngine import *
from plantDiseaseAI.backend.LangCore import *
import plantDiseaseAI.backend.lex as lex
import plantDiseaseAI.backend.yacc as yacc
import pprint

pp = pprint.PrettyPrinter(indent = 2)

class TraverseContext(object):
    def __init__(self, spanGraph):
        self._path = []
        self._continued = True
        self._matched = False
        self._inputGraph = spanGraph
        self._deadStates = {}
        self._hitSequence = []

        pp.pprint(self._inputGraph._startMap)

    def isEnd(self, pos):
        if pos in self._inputGraph._startMap:
            return False
        else:
            return True

class RuleTagger(Tagger):
    def __init__(self):
        self._graph = None

    def loadRules(self, ruleFile):
        with open(ruleFile, 'r') as fd:
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
            if spanId is None:
                continue
            for act in edge._actions:
                if act._astAction._type == 'Slot':
                    if 'slots' in seq._annotation:
                        if act._astAction._k in  seq._annotation['slots']:
                            seq._annotation['slots'][act._astAction._k].append(ctx._inputGraph._spans[spanId]._text)
                        else:
                            seq._annotation['slots'][act._astAction._k] = [ctx._inputGraph._spans[spanId]._text]
                    else:
                        seq._annotation['slots'] = {}
                        seq._annotation['slots'][act._astAction._k] = [ctx._inputGraph._spans[spanId]._text]
                elif act._astAction._type == 'General':
                    seq._annotation[act._astAction._k] = act._astAction._v
                else:
                    raise TypeError('unknown action type:[' + act._astAction._type + ']')
    def walk(self, pos, node, ctx):
        print 'walk on: [pos:' + str(pos) +'] [node:' + str(node._id) + ']'
        ctx._matched = False
        # check dead states
        state_sig = str(node._id) + '-' + str(pos)
        if state_sig in ctx._deadStates:
            print 'Debug: deadState[' + state_sig + ']' 
            return
        # match a final state
        if (node.endNode() == True) and ctx.isEnd(pos):
            print 'Debug: Matched a final state'
            ctx._matched = True
            # generate sequence
            seq = Sequence()
            seq._source = 'RuleTagger'
            seq._prob = '0.9' #hardcode
            for (spanId, edge) in ctx._path:
                if spanId != None:
                    seq._spans.append(spanId)
            ctx._hitSequence.append(seq)
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
                    ctx._path.pop()
                else:
                    if pos not in ctx._inputGraph._startMap:
                        matched = False
                        break
                    # Find the overlap of edges
                    spanEdges = ctx._inputGraph._startMap[pos]
                    for spanId in spanEdges:
                        inputSpan = ctx._inputGraph._spans[spanId]
                        if self.matchEdge(inputSpan, edge._predicate):
                            ctx._path.append((spanId, edge))
                            self.walk(pos + inputSpan._len, edge._dest, ctx)
                            ctx._matched = (ctx._matched or matched)
                            ctx._path.pop()
                            if isinstance(edge._predicate, AtomPredicate):
                                break
            ctx._matched = matched
            if matched == False:
                ctx._deadStates[str(node._id) + '-' + str(pos)] = 1

    def matchEdge(self, span, pred):
        if isinstance(pred, AtomPredicate):
            return (span._type == 'tok')
        elif isinstance(pred, SpanPredicate):
            if span._type == pred._type:
                for (k,v) in pred._checks.items():
                    if v == '':
                        if k in span._attrs:
                            pass
                        else:
                            return False
                    else:
                        if k in span._attrs:
                            if span._attrs[k] == v:
                                pass
                            else:
                                return False
                        else:
                            return False
                return True
            else:
                return False
        elif isinstance(pred, TokenValuePredicate):
            if span._type != 'tok':
                return False
            else:
                return (span._text == pred._val)
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
        ctx = TraverseContext(spanGraph)
        self.walk(0, self._graph._startNode,ctx)
        for s in ctx._hitSequence:
            seqList.append(s)
