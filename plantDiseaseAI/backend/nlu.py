# -*- coding: utf-8 -*-
from Tagging import *
import hanzi
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
        self._taggers = []
    def text_preprocess(self, phrases, rawText):
        sentList = re.split('[' + hanzi.nlu_stops +']+', rawText.strip())
        for sentIdx in range(len(sentList)):
            sent = sentList[sentIdx]
            if sent == '':
                continue
            #print "[debug]: " + sent.encode('utf-8')
            subsentList = re.split('[' + hanzi.phrase_delim + ']+', sent.strip())
            for ssIdx in range(len(subsentList)):
                ss = subsentList[ssIdx]
                ss_rewrite =  re.sub(r'\[\d*-?\d*\]','',ss)
                ss_rewrite =  re.sub(r'\s','',ss_rewrite)
                if ss_rewrite != '':
                    phrases.append(ss_rewrite)

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
