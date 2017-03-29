#!/usr/bin/python
import sys,os
import pprint

from ruleLex import *
from ruleParser import *
from AST import *
from Graph import *
import decimal

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__': 
    filename = sys.argv[1]
    graphFile = 'graph.dot'
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
        ast.dumpOrderedAST()
        ast.expand()
        ast.dumpAST()
        '''
        #pp.pprint(result)
        graph = Graph()
        graph.buildGraph(ast)
        graph.dump(graphFile)
        '''
