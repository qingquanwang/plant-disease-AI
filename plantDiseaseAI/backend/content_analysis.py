# -*- coding: utf-8 -*-
import os,sys
import json
import pprint
import nltk.data
import re
import copy
from clu.content import hanzi

pp = pprint.PrettyPrinter(indent = 4)

english_pickle_path = 'tokenizers/punkt/english.pickle'

class ContentAnalysis(object):

    def __init__(self, data_root):
        self._data_root = data_root
        self._sent_detector_english = nltk.data.load(
            os.path.join(self._data_root, english_pickle_path))

    def content_to_sentences_chinese(self, text):
        return re.split('[' + hanzi.stops +']+', text.strip())

    def sentence_to_subsent_chinese(self, text):
        return re.split('[' + hanzi.phrase_delim + ']+', text.strip())

    # phrase rewrite: 
    #   - remove reference : [1-2]
    def phrase_rewrite(self, phrase):
        return re.sub(r'\[\d*-?\d*\]','',phrase)

    # return a list of sentence , a sentece is a list of phrase
    def content_to_phrase(self, text):
        res = []
        for sent in re.split('[' + hanzi.stops +']+', text.strip()):
            ss_list = []
            for ss in re.split('[' + hanzi.phrase_delim + ']+', sent.strip()):
                ss_rewrite = self.phrase_rewrite(ss)
                if ss_rewrite != '':
                    ss_list.append(ss_rewrite)
            if len(ss_list) > 0:
                res.append(copy.copy(ss_list))
        return res

    # serialize the content
    def serialize_content(self, text):
        res = []
        sents = self.content_to_phrase(text)
        for s in sents:
            res.append('\001'.join(s))
        return '\002'.join(res)
