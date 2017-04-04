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
    def dump(self, inputGraph):
        res = []
        for idx in self._spans:
            span = inputGraph._spans[idx]
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
