# -*- coding: utf-8 -*-
import pprint

pp = pprint.PrettyPrinter(indent = 2)

class Token(object):
    def __init__(self, text, t):
        if isinstance(text, unicode):
            text = text.encode(encoding='utf-8')
        self._text = text
        self._type = t

    def __repr__(self):
        return 'Token({}, {})'.format(self._text, self._type)

class Preprocessor(object):
    def __init__(self):
        pass

    def preprocess(self, rawText, toks):
        pass

class Span(object):
    _start = 0
    _len = 0
    _type = 'tok'
    _text = ''
    _attrs = {}
    def __init__(self, start, l, t, text):
        self._start = start
        self._len = l
        self._type = t
        self._text = text
    def dump(self):
        res = []
        res.append(str(self._start))
        res.append(str(self._len))
        res.append(str(self._type))
        res.append(str(self._text))
        return '[' + ':'.join(res) +']'

def Sequence(object):
    def __init__(self):
        self._spans = []
        self._annotation = {}
        self._source = ''
        self._prob = 0.0

def Tagger(object):
    def __init__(self):
        pass
    # seqList = [ Sequence ]
    def tag(self, spanGraph, seqList):
        pass
