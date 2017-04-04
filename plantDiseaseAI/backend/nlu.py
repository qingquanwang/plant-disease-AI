# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.LangCore import *
from plantDiseaseAI.backend.Tagging import *
from plantDiseaseAI.backend.preprocessor import *
from plantDiseaseAI.backend.tagger import *
import re
import pprint

pp = pprint.PrettyPrinter(indent = 2)

# NLU result of each query or short text
class Analysis(object):
    def __init__(self, graph, seqs):
        self._graph = graph
        self._seqs = seqs
    def dedupRank(self):
        dedupedSeq = []
        sigHash = {}
        for seq in self._seqs:
            sig = seq.getSignature()
            if sig not in sigHash:
                dedupedSeq.append(seq)
                sigHash[sig] = len(dedupedSeq) - 1
            else:
                if seq._prob > dedupedSeq[sigHash[sig]]._prob:
                    dedupedSeq[sigHash[sig]] = seq
        sorted(dedupedSeq, key = lambda seq : seq._prob, reverse=True)
        self._seqs = dedupedSeq

    def dumpBestSeq(self, dump_tagger=False):
        if len(self._seqs) > 0:
            if dump_tagger:
                return self._seqs[0].dump(self._graph) + '\002' + self._seqs[0]._source
            else:
                return self._seqs[0].dump(self._graph)
        else:
            return ''

    def getBestSeq(self, threshold):
        if len(self._seqs) > 0:
            if self._seqs[0]._prob > threshold:
                return self._seqs[0]
            else:
                return None
        else:
            return None

class NLU(object):
    def __init__(self, dic):
        self._dic = dic
        self._preprocessor = ZhBookPreprocessor()
        self._taggers = []
    def setPreprocessor(self, preprocessorName):
        if preprocessorName == 'zhBook':
            self._preprocessor = ZhBookPreprocessor()
        else:
            raise NameError('unknown preprocessor: ' + preprocessorName)

    def appendTagger(self, tagger):
        self._taggers.append(tagger)

    # tokens are input after preprocessing
    def tagTokens(self, toks):
        inputGraph = SpanGraph()
        inputGraph.constructGraph(self._dic, toks)
        #for span in inputGraph._spans:
        #    print 'Debug:' + span.dump().encode('utf-8')
        seqs = []
        for tagger in self._taggers:
            tagger.tag(inputGraph, seqs)
        ana = Analysis(inputGraph, seqs)
        ana.dedupRank()
        return ana

    # text is input before preprocessing
    def tagText(self, anaList, rawText, split = True):
        toks = []
        self._preprocessor.preprocess(rawText, toks)
        bufferedToks = []
        
        for tok in toks:
            if tok._type == 'splitter':
                if split == True:
                    anaList.append(self.tagTokens(bufferedToks))
                    bufferedToks[:] = []
                else:
                    bufferedToks.append(tok)
            else:
                bufferedToks.append(tok)
        if len(bufferedToks) > 0:
            anaList.append(self.tagTokens(bufferedToks))
