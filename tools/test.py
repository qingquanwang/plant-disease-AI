#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import pprint
import os,sys
from os.path import realpath, join, dirname
sys.path.insert(0, join(dirname(realpath(__file__)), '../'))
from plantDiseaseAI.backend.preprocessor import *
from plantDiseaseAI.backend.tagger import *
from plantDiseaseAI.backend.Tagging import *
from plantDiseaseAI.backend.rewriter import *

pp = pprint.PrettyPrinter(indent=2)

if __name__ == '__main__':
    dic = DictManager()
    dic.load_dict('./data/test/name.dic')
    #pp.pprint(dic._names)
    graph = SpanGraph()
    #text = u'abcdef'
    #text = u'a ab,def。cde"sdfsadfasdd" 3.0'
    #text = u'天津传说中的网上办事大厅怎么走'
    text = u'2014天津失业保险条例'
    tokens = []
    preprocessor = ZhBookPreprocessor()
    preprocessor.preprocess(text, tokens)

    graph.constructGraph(dic, tokens)
    #pp.pprint(graph.getSpans(True))
    for s in graph._spans:
        print s.dump()
    pp.pprint(graph._startMap)

    print 'XXXXX'
    rewriter = RemoveTokRewriter()
    inputGraph = rewriter.rewrite(graph)
    for s in inputGraph._spans:
        print s.dump()
    pp.pprint(inputGraph._startMap)
    seq = []
    #graph.greedySeq(seq, 0, True)
    tagger = GreedyTagger()
    tagger.tag(inputGraph, seq)
    pp.pprint(seq[0])

    res = []
    for idx in seq[0]._spans:
        print idx
        span = inputGraph._spans[idx]
        res.append('[' + span._text + '|' + span._type + ']')
    print ''.join(res)
