# -*- coding: utf-8 -*-
import pprint
import json
pp = pprint.PrettyPrinter(indent = 2)

class Token(object):
    def __init__(self, text, t):
        self._text = text
        self._type = t
        self._lang = 'zh'
    # 'en' 'zh' for tok, other span is 'other'
    def setLang(self, lang):
        self._lang = lang

    def __repr__(self):
        return 'Token({}, {})'.format(self._text.encode('utf-8'), self._type)

    def __str__(self):
        return '({}, {})'.format(self._text.encode('utf-8'), self._type)

class Preprocessor(object):
    def __init__(self):
        pass

    def preprocess(self, rawText, toks):
        pass

class Span(object):
    def __init__(self, start, l, t, text):
        self._start = start
        # Note that, _len is the number of taken tokens, not really the length of text
        self._len = l
        self._type = t
        self._text = text
        self._lang = 'other'
        self._attrs = {}
    def setLang(self, lang):
        self._lang = lang
    def dump(self):
        res = []
        res.append(str(self._start))
        res.append(str(self._len))
        res.append(self._type)
        res.append(self._text)
        return '[' + ':'.join(res) +']'

class Sequence(object):
    def __init__(self):
        # spanId collection in order
        self._spans = []
        self._annotation = {}
        self._source = ''
        self._prob = 0.0
    def serializeAnn(self):
        return json.dumps(self._annotation)
    def getSignature(self):
        sig = []
        for spanId in self._spans:
            sig.append(str(spanId))
        return '-'.join(sig)
    def dump(self, inputGraph, removeTok = False):
        res = []
        for idx in self._spans:
            span = inputGraph._spans[idx]
            if removeTok and span._type == 'tok':
                continue
            else:
                res.append('[' + span._text + '|' + span._type + ']')
        return ''.join(res) + '\002' + self.serializeAnn()
# Annotation on tagging sequence:
#   slots: slot->list[spanId]
#   conclusion: k->v
class Annotation(object):
    def __init__(self):
        self._slots = {}
        self._conclusion = {}
    def setConclusion(self, k, v):
        self._conclusion[k] = v
    def appendSlot(self, k, v):
        if k in self._slots:
            if v not in self._slots[k]:
                self._slots[k].append(v)
        else:
            self._slots[k] = []
            self._slots[k].append(v)

class Tagger(object):
    def __init__(self):
        pass
    # seqList = [ Sequence ]
    def tag(self, spanGraph, seqList):
        pass

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

        self._seqs = sorted(dedupedSeq, key = lambda seq : seq._prob, reverse=True)


    def dumpAllSeq(self):
        res = []
        for seq in self._seqs:
            res.append(seq.dump(self._graph) + '\002' + seq._source + '\002' + str(seq._prob))
        return '\003'.join(res)

    def dumpBestSeq(self, dump_tagger=False, removeTok=False):
        if len(self._seqs) > 0:
            if dump_tagger:
                return self._seqs[0].dump(self._graph, removeTok) + '\002' + self._seqs[0]._source
            else:
                return self._seqs[0].dump(self._graph, removeTok)
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

class Semantic(object):
    def __init__(self):
        pass
    def extract(self, anaList, semantics):
        pass
