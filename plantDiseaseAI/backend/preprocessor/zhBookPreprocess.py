# -*- coding: utf-8 -*-
import pprint

pp = pprint.prettyPrinter(indent = 2)

tokens = (
    'DIGIT',
    'Zh-Word',
    'En-Word',
    'SplitPunct',
    'UnsplitPunct',
    'WordsQuot',
    'BookQuo',
    'Reference'
)

def ZhBookPreprocessor(object):
    def __init__(self):
        pass

    def preprocess(self, rawText, toks):
        pass
