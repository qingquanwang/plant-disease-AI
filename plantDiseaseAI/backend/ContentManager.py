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
        self._plants = []
        self._startId = 0
        self._idPrefix = 'BBP'
        self._docType = '/plants'

    def filterByFileName(self, fileName):
        return False

    # load all document:
    #    extract ContentIndex for each document
    #    generate ContentPool object and put into the ContentPool
    def process(self, pool):
        for fileName in os.listdir(self._docRoot):
            self.process_single_file(os.path.join(self._docRoot, fileName), pool)
    
    def process_single_file(self, fileName, pool):
        #1. check name
        if self.filterByFileName(fileName):
            sys.stderr.write("Filtered By FileName: " + fileName + '\n')
            return
        #2. load file => generate document
        with open(fileName, 'r') as fd:
            obj = json.load(fd, encoding = 'utf-8')
            docId = self._idPrefix + '-' + str(self._startId)
            self._startId = self._startId + 1
            doc = ContentDoc(docId, self._docType, fileName, json.dumps(obj, encoding='utf-8'))
            #3. generate Plant object and generate index for the doc
            p = Plant(obj['name'])
            self._plants.append(p)
            idx = ContentIndex('/plantName', p._plantName, 1.0)
            pool.insertDoc(idx, doc)
            return

class BaiduBaikeDisease(object):
    # docRoot: content/baidu/baike-diseases
    def __init__(self, docRoot, ca):
        self._docRoot = docRoot
        self._ca = ca
        self._diseases = []
        self._startId = 0
        self._idPrefix = 'BBD'
        self._docType = '/diseases'

    def filterByFileName(self, fileName):
        filename = filename.decode('utf-8')
        toks = filename.split('.')
        if len(toks) != 2:
            return True
        fn = toks[0]
        if toks[1] != 'json':
            return True
        if not fn.endswith((u'病')):
            return True
        #remove poem title
        if (u'·') in fn:
            return True
        if len(fn) <= 3:
            return True
        return False

    def process(self, pool):
    def is_symptom(self, key):
        symptom_intents = [u'病症', u'病状', u'发病', u'症状']
        for s in symptom_intents:
            if s in key:
                return True
        return False
    def process_single_file(self, fileName, pool):
        if self.filterByFileName(fileName):
            sys.stderr.write("Filtered By FileName: " + fileName + '\n')
            return
        with open(fileName, 'r') as fd:
            obj = json.load(fd, encoding = 'utf-8')
            docId = self._idPrefix + '-' + str(self._startId)
            self._startId = self._startId + 1
            doc = ContentDoc(docId, self._docType, fileName, json.dumps(obj, encoding='utf-8'))
            for key in obj['h2']:
                if not self.is_symptom(key):
                    continue
                


class ContentManager(object):
    def __init__(self, docRoot):
        self._docRoot = docRoot
    def process_content():
        #1
