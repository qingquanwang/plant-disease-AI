# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.LangCore import *
import pprint

pp = pprint.PrettyPrinter(indent = 2)

# span linked graph
class SpanGraph(object):
    def __init__(self):
        # spanId -> list(child span id)
        self._next = {}
        # spanId -> span
        self._spans = []
        # start_pos -> list(spanId)
        self._startMap = {}
    
    def createGraphFromSpan(self, spans):
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
            dummySpan = Span(i, 1, 'tok', tokens[i])
            spans.append(dummySpan)
            # process range [i, min(length-1, i+max_ngram-1)]
            for j in reversed(range(max_ngram)):
                if i+j >= length:
                    continue
                ngram = ''.join(tokens[i:i+j+1])
                #print "[debug] current ngram:" + ngram
                candidates = dic.lookup(ngram)
                if len(candidates) == 0:
                    continue
                for cand in candidates:
                    span = Span(i, j+1, cand._type, ngram)
                    spans.append(span)
                # only keep the longest shot for each start position
                break
        self.createGraphFromSpan(spans)

    def filteredTokens(self, tokens, filtered_tokens):
        filtered_tokens[:] = []
        for tok in tokens:
            if tok._type == 'tok':
                filtered_tokens.append(tok)
            elif tok._type.startswith('/'):
                filtered_tokens.append(tok)
            else:
                # filtered
                pass
    
    # en en will be collapsed
    def generateNgram(self, i, j, tokens):
        # tokens[i:i+j+1]
        toks = []
        for l in range(j+1):
            if tokens[i+l]._type in ['splitter', 'punct']:
                return ''
            else:
                toks.append(tokens[i+l]._text)
        return ''.join(toks)

    def constructGraph(self, dic, tokens, max_ngram = 5):
        # use tok list generated from preprocessor to construct graph
        filtered_tokens = []
        self.filteredTokens(tokens, filtered_tokens)
        length = len(filtered_tokens)
        spans = []
        for i in range(length):
            dummySpan = Span(i, 1, filtered_tokens[i]._type, filtered_tokens[i]._text)
            spans.append(dummySpan)
            
            # process range [i, min(length-1, i+max_ngram-1)]
            for j in reversed(range(max_ngram)):
                if i+j >= length:
                    continue
                #ngram = ''.join(tokens[i:i+j+1])
                ngram = self.generateNgram(i, j, filtered_tokens)
                if ngram == '':
                    continue
                #print "[debug] current ngram:" + ngram
                candidates = dic.lookup(ngram)
                if len(candidates) == 0:
                    continue
                for cand in candidates:
                    span = Span(i, j+1, cand._type, ngram)
                    spans.append(span)
                # only keep the longest shot for each start position
                break
        self.createGraphFromSpan(spans)

    # dump sequence from list(spanId)
    def dump_seq(self, seq):
        res = []
        for idx in seq:
            span = self._spans[idx]
            res.append('[' + span._text + ':' + span._type + ']')
        return ''.join(res)
    # return the list of spans regardless of the conflict
    def getSpans(self, include_token = False):
        if include_token:
            return self._spans
        res = []
        for span in self._spans:
            if span._type != 'tok':
                res.append(span)
        return res

    # Always use the longest span at each position
    def greedySeq(self, seq, pos = 0, include_token = False):
        # Find non-trivial span first
        if pos not in self._startMap:
            return
        spanIdList = self._startMap[pos]
        longest_spanId = -1
        max_span_len = -1
        trivial_spanId = -1
        for spanId in spanIdList:
            if self._spans[spanId]._type == 'tok':
                trivial_spanId = spanId
            else:
                if self._spans[spanId]._len > max_span_len:
                    max_span_len = self._spans[spanId]._len
                    longest_spanId = spanId
        if max_span_len > 0:
            seq.append(longest_spanId)
            next_pos = self._spans[longest_spanId]._start + self._spans[longest_spanId]._len
            return self.greedySeq(seq, next_pos, include_token)
        else:
            if include_token:
                seq.append(trivial_spanId)
            return self.greedySeq(seq, self._spans[trivial_spanId]._start + 1, include_token)
