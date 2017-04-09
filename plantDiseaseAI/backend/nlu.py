# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.LangCore import *
from plantDiseaseAI.backend.Tagging import *
from plantDiseaseAI.backend.preprocessor import *
from plantDiseaseAI.backend.tagger import *
import re
import pprint

pp = pprint.PrettyPrinter(indent = 2)

class NLU(object):
    def __init__(self, dic):
        self._dic = dic
        self._preprocessor = ZhBookPreprocessor()
        self._taggers = []
    def setPreprocessor(self, preprocessorName):
        if preprocessorName == 'zhBook':
            self._preprocessor = ZhBookPreprocessor()
        else:
            raise NameError('unknown preprocessor: ' + preprocessorName)

    def appendTagger(self, tagger):
        self._taggers.append(tagger)

    # tokens are input after preprocessing
    def tagTokens(self, toks):
        inputGraph = SpanGraph()
        inputGraph.constructGraph(self._dic, toks)
        #for span in inputGraph._spans:
        #    print 'Debug:' + span.dump().encode('utf-8')
        seqs = []
        for tagger in self._taggers:
            tagger.tag(inputGraph, seqs)
        ana = Analysis(inputGraph, seqs)
        ana.dedupRank()
        return ana

    # text is input before preprocessing
    def tagText(self, anaList, rawText, split = True):
        toks = []
        self._preprocessor.preprocess(rawText, toks)
        bufferedToks = []
        
        for tok in toks:
            if tok._type == 'splitter':
                if split == True:
                    anaList.append(self.tagTokens(bufferedToks))
                    bufferedToks[:] = []
                else:
                    bufferedToks.append(tok)
            else:
                bufferedToks.append(tok)
        if len(bufferedToks) > 0:
            anaList.append(self.tagTokens(bufferedToks))
