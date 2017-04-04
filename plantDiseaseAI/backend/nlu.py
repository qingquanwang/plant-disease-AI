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
    def __init__(self, query, graph):
        self._text = query
        self._graph = graph
        self._bestSeqIndex = -1
        # seq list
        self._candidateSeqList = []
        self._scoreList = []
    def appendCandidate(self, seq, tagger_prob, tagger_type, annotation=None):
        self._candidateSeqList.append((seq, tagger_prob, tagger_type, annotation))
    def dedupRank(self):
        #TO DO: dedup and scoring
        # pick up the best seq
        max_score = -1.0
        for (seq, tagger_prob, tagger_type, annotation) in self._candidateSeqList:
            if tagger_type == 'GreedyTagger':
                self._scoreList.append(0.6)
            else:
                self._scoreList.append(0.1)
        for i in range(len(self._scoreList)):
            if self._scoreList[i] > max_score:
                max_score = self._scoreList[i]
                self._bestSeqIndex = i
        return
    def dumpBestSeq(self, dump_tagger=False):
        (seq, tagger_prob, tagger_type, annotation) = self._candidateSeqList[self._bestSeqIndex]
        if dump_tagger:
            return self._graph.dump_seq(seq) + ':' + tagger_type
        else:
            return self._graph.dump_seq(seq)
    def getBestSeq(self, threshold):
        if self._bestSeqIndex < 0:
            return (None, None)
        (seq, tagger_prob, tagger_type, annotation) = self._candidateSeqList[self._bestSeqIndex]
        if self._scoreList[self._bestSeqIndex] > threshold:
            spans = []
            for spanId in seq:
                spans.append(self._graph._spans[spanId])
            return (spans, annotation)
        else:
            return (None, None)
class NLU(object):
    def __init__(self, dic):
        self._dic = dic
        self._preprocessor = None
        self._taggers = []
    def setPreprocessor(self, preprocessorName):
        if preprocessorName == 'zhBook':
            return ZhBookPreprocessor()
        else:
            raise NameError('unknown preprocessor: ' + preprocessorName)

    def appendTagger(self, taggerName):
        if taggerName == 'greedy':
            tagger = GreedyTagger()
            self._taggers.append(tagger)
        elif taggerName == 'ruleEngine':
            tagger = RuleTagger()
            self._taggers.append(tagger)
        else:
            raise NameError('unknown tagger: ' + taggerName)

    # tokens are input after preprocessing
    def tagTokens(self, toks):

    # text is input before preprocessing
    def tagText(self, rawText, split == True):

    def analysis(self, rawText):

        phrases = []
        self.text_preprocess(phrases, rawText)
        anaList = []
        for text in phrases:
            ana = self.analysis_single_text(text)
            if ana._bestSeqIndex >= 0:
                anaList.append(ana)
        return anaList
    def analysis_single_text(self, text):
        #print "[debug]:" + text.encode('utf-8')
        #1. dic tagging -> graph
        graph = SpanGraph()
        graph.createGraph(self._dic, text)
        ana = Analysis(text, graph)
        #2. native greedy tagger
        native_seq = []
        graph.greedySeq(native_seq, 0, True)
        ana.appendCandidate(native_seq, 0.6, 'GreedyTagger', None) 
        #TODO: 3. seq candidates generation with different Taggers(CRF/RNN/Autometa/Reduce)
        # 4. Dedup and rerank
        ana.dedupRank()
        return ana
