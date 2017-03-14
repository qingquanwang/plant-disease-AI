# -*- coding: utf-8 -*-
import json
import re
import copy
import hanzi
import ContentIndex

# Content Analysis: common content processing functions, 
#                   Feature Extraction, dict load, tagging, filtering
# All static data of content processing is maintained by this class object
class ContentAnalysis(object):
    def __init__(self, dataRoot):
        self._dataRoot = dataRoot

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

# Plant Entries: extract plant entity
class BaiduBaikePlant(object):
    # docRoot: content/baidu/baike-plants
    def __init__(self, docRoot, ca):
        self._docRoot = docRoot
        self._ca = ca
        

    def filterByFileName(self, fileName):
        return False

    def loadAll

class BaiduBaikeDisease(object):



class ContentManager(object):
    def __init__(self, docRoot):
        self._docRoot = docRoot
    def process_content():
        #1
