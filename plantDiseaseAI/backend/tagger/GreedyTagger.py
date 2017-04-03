# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.LangCore import *
from plantDiseaseAI.backend.Tagging import *

import pprint

pp = pprint.PrettyPrinter(indent = 2)

class GreedyTagger(Tagger):
    def __init__(self):
        pass
    def tag(self, spanGraph, seqList):
        seq = Sequence()
        seq._source = 'GreedyTagger'
        seq._prob = 0.6
        spanGraph.greedySeq(seq._spans, 0, False)
        seqList.append(seq)
