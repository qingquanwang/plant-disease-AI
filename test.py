#!/usr/bin/python
import argparse
import pprint
import os,sys
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.Tagging import *

pp = pprint.PrettyPrinter(indent=2)

if __name__ == '__main__':
    dic = DictManager()
    dic.load_dict('./data/test/name.dic')
    pp.pprint(dic._names)
    graph = SpanGraph()
    #text = u'abcdef'
    text = u'def'
    graph.createGraph(dic, text)
    #pp.pprint(graph.getSpans(True))
    for s in graph._spans:
        print s.dump()
    pp.pprint(graph._startMap)
    seq = []
    graph.greedySeq(seq, 0, True)
    pp.pprint(seq)

    res = []
    for idx in seq:
        span = graph._spans[idx]
        res.append('[' + span._text + '|' + span._type + ']')
    print ''.join(res)
