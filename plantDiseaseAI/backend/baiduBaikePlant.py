# -*- coding: utf-8 -*-
import os,sys
import json
import pprint
import re
from clu.content.content_analysis import ContentAnalysis

pp = pprint.PrettyPrinter(indent = 4)

symptom_intents = [
    u'病症',
    u'病状',
    u'发病',
    u'症状'
]

class BaiduBaikePlant():
    def __init__(self, inputDir, data_root):
        self._inputDir = inputDir
        self._ca = ContentAnalysis(data_root)
    
    def filterByFileName(self,filename):
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
    def cleanup(self):
        for fileName in os.listdir(self._inputDir):
            if self.filterByFileName(fileName):
                sys.stderr.write("Filtered By FileName:" + fileName +'\n')
                continue
            with open(os.path.join(self._inputDir, fileName)) as fd:
                raw_obj = json.load(fd, encoding = 'utf-8')
                for key in raw_obj['h2']:
                    for s in symptom_intents:
                        if s in key:
                            #sents = self._ca.content_to_sentences_chinese(raw_obj['h2'][key])
                            #print "===================" + key.encode('utf-8') + "========================="
                            #print raw_obj['h2'][key].encode('utf-8')
                            #print "---------------------------------------------"
                            sents = self._ca.content_to_phrase(raw_obj['h2'][key])
                            for sent in sents:
                                for phrase in sent:
                                    print phrase.encode('utf-8')



                            #print self._ca.serialize_content(raw_obj['h2'][key]).encode('utf-8')
                            print "\n"
                            break
                            #print raw_obj['h2'][key].encode('utf-8')
        return

    def normalize(self):
        return

    def save(self, outputDir):
        return
