#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import pprint
import os,sys
from plantDiseaseAI.backend.preprocessor import *
from plantDiseaseAI.backend.tagger import *
from plantDiseaseAI.backend.Tagging import *

pp = pprint.PrettyPrinter(indent=2)

if __name__ == '__main__':
    dic = DictManager()
    dic.load_dict('./data/test/name.dic')
    pp.pprint(dic._names)
    graph = SpanGraph()
    #text = u'abcdef'
    text = u'a ab,def。cde"sdfsadfasdd" 3.0'
    
    tokens = []
    preprocessor = ZhBookPreprocessor()
    preprocessor.preprocess(text, tokens)

    graph.constructGraph(dic, tokens)
    #pp.pprint(graph.getSpans(True))
    for s in graph._spans:
        print s.dump()
    pp.pprint(graph._startMap)
    seq = []
    #graph.greedySeq(seq, 0, True)
    tagger = GreedyTagger()
    tagger.tag(graph, seq)
    pp.pprint(seq[0])

    res = []
    for idx in seq[0]._spans:
        span = graph._spans[idx]
        res.append('[' + span._text + '|' + span._type + ']')
    print ''.join(res)
