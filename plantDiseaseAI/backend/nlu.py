# -*- coding: utf-8 -*-
from Tagging import *
import hanzi
import re

# NLU result of each query or short text
class Analysis(object):
    def __init__(self, query, graph):
        self._text = query
        self._graph = graph
        self._bestSeqIndex = -1
        # seq list
        self._candidateSeqList = []
        self._scoreList = []
    def appendCandidate(seq, tagger_prob, tagger_type):
        self._candidateSeqList.append((seq, tagger_prob, tagger_type))
    def dedupRank():
        #TO DO: dedup and scoring
        # pick up the best seq
        max_score = -1.0
        for (seq, tagger_prob, tagger_type) in self._scoreList:
            if tagger_type == 'GreedyTagger':
                self._scoreList.append(0.6)
            else:
                self._scoreList.append(0.1)
        for i in len(self._scoreList):
            if self._scoreList[i] > max_score:
                max_score = self._scoreList[i]
                self._bestSeqIndex = i
        return
    def dumpBestSeq():

class NLU(object):
    def __init__(self, dic):
        self._dic = dic
        self._taggers = []
    def text_preprocess(self, phrases, rawText):
        for sent in re.split('[' + hanzi.stops +']+', text.strip()):
            ss_list = []
            for ss in re.split('[' + hanzi.phrase_delim + ']+', sent.strip()):
                ss_rewrite =  re.sub(r'\[\d*-?\d*\]','',ss)
                if ss_rewrite != '':
                    ss_list.append(ss_rewrite)
            if len(ss_list) > 0:
                phrases.append(copy.copy(ss_list))

    def analysis(self, rawText):
        phrases = []
        self.text_preprocess(phrases, rawText)
        anaList = []
        for text in phrases:
            ana = self.analysis_single_text(text)
            if len(ann._bestSeqIndex) > 0:
                anaList.append(ana)
        return anaList
    def analysis_single_text(self, text):
        #1. dic tagging -> graph
        graph = SpanGraph()
        graph.createGraph(self._dic, text)
        ana = Analyis(text, graph)
        #2. native greedy tagger
        greedySeq = []
        graph.greedySeq(greedySeq, 0, True)
        ana.appendCandidate(greedySeq, 0.6, 'GreedyTagger') 
        #TODO: 3. seq candidates generation with different Taggers(CRF/RNN/Autometa/Reduce)
        # 4. Dedup and rerank
        ana.dedupRank()
        return ana
