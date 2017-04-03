#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import pprint
import os,sys
from plantDiseaseAI.backend.preprocessor import *
from plantDiseaseAI.backend.tagger import *
from plantDiseaseAI.backend.Tagging import *
import plantDiseaseAI.backend.yacc as yacc
import plantDiseaseAI.backend.lex as lex

pp = pprint.PrettyPrinter(indent=2)


def createPreprocessor(name):
    if name == 'zhBook':
        return ZhBookPreprocessor()
    else:
        raise NameError('Unknown name of preprocessor:[' + name + ']')

def investigation_rule(filename):
    with open(filename, 'r') as fd:
        data = fd.read().decode('utf-8')
        lexer = lex.lex(debug=1, optimize=0, lextab='lextab', reflags=0)
        lexer.input(data)

        parser = yacc.yacc()
        result = parser.parse(lexer=lexer)
        ast = AST(result)
        print "\n\nOriginal AST:"
        ast.dumpOrderedAST()
        ast.expand()
        print "\n\nNormalized AST:"
        ast.dumpAST()

        graph = Graph()
        graph.buildGraph(ast)
        graph.dump('graph.dot')

def tagToks(toks, tagger, dic):
    inputGraph = SpanGraph()
    inputGraph.constructGraph(dic, toks)
    for span in inputGraph._spans:
        print 'Debug:' + span.dump().encode('utf-8')
    seqs = []
    tagger.tag(inputGraph, seqs)
    seq_res = []
    for seq in seqs:
        res = []
        for idx in seq._spans:
            span = inputGraph._spans[idx]
            res.append('[' + span._text + '|' + span._type + ']')
        seq_res.append(''.join(res) + '\002' + seq.serializeAnn())
    print '\001'.join(seq_res).encode('utf-8')

def processToks(toks, split, tagger, dic):
    res = []
    for tok in toks:
        if tok._type == 'splitter':
            if split == True:
                tagToks(toks, tagger, dic)
                res[:] = []
            else:
                res.append(tok)
        else:
            res.append(tok)
    if len(res) > 0:
        tagToks(toks, tagger, dic)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
                description='ruleEngine debug or process text', usage='''
                ./ruleEngine.py --r ruleFile
                                --v [dump AST tree to stdout, and generate graph.dot]
                                --d dic
                                --i input
                                --p preprocessor
                                --s"
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--r', type=str,
                        default='data/test/RuleEngine/rule0',
                        help='rule file')

    parser.add_argument('--v', dest = 'v', action = 'store_true')

    parser.add_argument('--d', type=str,
                        default='data/test/name.dic',
                        help='dictionary')

    parser.add_argument('--i', type=str,
                        default='-',
                        help='input file or - (stdin)')

    parser.add_argument('--p', type=str,
                        default='zhBook',
                        help='[zhBook]')

    parser.add_argument('--s', dest = 's', action = 'store_true')

    args = parser.parse_args()

    ruleFile = args.r

    if args.v:
        # investigation mode
        investigation_rule(ruleFile)
        sys.exit(0)

    # create preprocessor
    preprocessor = createPreprocessor(args.p)
    
    # load dictionary
    dic = DictManager()
    dicFile = args.d
    dic.load_dict(dicFile)

    # create Tagger
    tagger = RuleTagger()
    tagger.loadRules(ruleFile)

    # process input
    inputFile = args.i
    split = args.s
    if inputFile == '-':
        for line in sys.stdin.readlines():
            toks = []
            preprocessor.preprocess(line.strip('\n').decode('utf-8'), toks)
            processToks(toks, split, tagger, dic)
    else:
        with open(inputFile, 'r') as fd:
            for line in fd.readlines():
                rawText = line.decode('utf-8').strip('\n')
                toks = []
                preprocessor.preprocess(rawText, toks)
                processToks(toks, split, tagger, dic)
