# -*- coding: utf-8 -*-
from DictManager import *


class Span(object):
    def __init__(self):
        self._start = 0
        self._len = 0
        self._type = 'tok'
        self._text = ''
    def __init__(self, start, l, t, text):
        self._start = start
        self._len = l
        self._type = t
        self._text = text
    def __init__(self, start, l, text):
        self._start = start 
        self._len = l
        self._type = 'tok'
        self._text = text

# a list of spans
class Seq(object):
    def __init__(self):
        self._spans = []
    def appendSpan(self, s):
        self._spans.append(s)

# span linked graph
class SpanGraph(object):
    def __init__(self):
        # spanId -> list(child span id)
        self._next = {}
        # spanId -> span
        self._spans = []
        # start_pos -> list(spanId)
        self._startMap = {}
    
    def createGraph(self, spans):
        spanNum = len(spans)
        for i in range(spanNum):
            self._spans.append(spans[i])
            start = spans[i]._start
            if start not in self._startMap:
               self._startMap[start] = []
            self._startMap[start].append(i)

        for i in range(spanNum):
            child_start = start + self._spans[i]._len
            if child_start in self._startMap:
                for child in self._startMap[child_start]:
                    self._next.append(child)

    def createGraph(self, dic, text, max_ngram = 5):
        # break text into tokens
        tokens = list(text)
        length = len(tokens)
        spans = []
        for i in range(length):
            dummySpan = Span(i, 1, tokens[i])
            spans.append(dummySpan)
            # process range [i, min(length-1, i+max_ngram-1)]
            for j in reversed(range(max_ngram)):
                if i+j+1 > length:
                    break
                ngram = ''.join(tokens[i:i+j])
                candidates = dic.lookup(ngram)
                if len(candidates) == 0:
                    continue
                for cand in candiates:
                    span = Span(i, j, cand._type, ngram)
                    spans.append(span)
                # only keep the longest shot for each start position
                break
        self.createGraph(spans)

    def getSpans(self, include_token = False):

    def greedySeq(self, include_token = False):
