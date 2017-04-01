# -*- coding: utf-8 -*-
from ruleEngine import *
import pprint

pp = pprint.prettyprinter(indent = 2)

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

