#!/usr/bin/python

import argparse
import pprint
from sets import Set
import os,sys
from os.path import realpath, join, dirname
sys.path.insert(0, join(dirname(realpath(__file__)), '../..'))
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.semantic import *

pp = pprint.PrettyPrinter(indent = 2)

class GovTitleExtracter(object):
    def __init__(self):
        self._subject2id = {}
        self._role2id = {}
        self._org2id = {}
        self._indexes = {}
        self._docAttrs = {}
        self._content = {}

    def getIndexId(self, dic):
        for name in dic._names.keys():
            for entity in dic._names[name]:
                if entity._type == '/gov/subject':
                    self._subject2id[name] = entity._id
                elif entity._type == '/gov/role':
                    self._role2id[name] = entity._id
                elif entity._type == '/org/gov':
                    self._org2id[name] = entity._id
                else:
                    pass

    def genIndex(self, index, blocks):
        if 'subject' in blocks and (blocks['subject'] in self._subject2id):
            index.append('subject:' + self._subject2id[blocks['subject']])
        if 'role' in blocks and (blocks['role'] in self._role2id):
            index.append('role:' + self._role2id[blocks['role']])
        if 'service' in blocks:
            index.append('service:' + blocks['service'])
        if 'condition' in blocks:
            index.append('condition:' + blocks['condition'])
        if 'org' in blocks and blocks['org'] in self._org2id:
            index.append('org:' + self._org2id[blocks['org']])

    def loadIndex(self, indexFile):
        with open(indexFile, 'r') as fd:
            for line in fd.readlines():
                (key, value) = line.strip('\n').decode('utf-8').split('\t')
                if key.startswith('idx:'):
                    idx = key[4:]
                    docIds = value.split('\001')
                    self._indexes[idx] = docIds
                elif key.startswith('doc:'):
                    docId = key[4:]
                    attrs = value.split('\001')
                    self._docAttrs[docId] = attrs
                else:
                    raise NameError('unknown prefix of gov index file:' + key.encode('utf-8'))

    def loadContent(self, contentFile):
        with open(contentFile, 'r') as fd:
            for line in fd.readlines():
                (docId, url, title, description) = line.decode('utf-8').strip('\n').split('\t')
                self._content[docId] = {}
                self._content[docId]['url'] = url
                self._content[docId]['title'] = title
                self._content[docId]['desc'] = description

    def scoreDocAttr(self, candset, attrs, scores):
        attrset = Set(attrs)
        for cand in candset:
            docAttrs = self._docAttrs[cand]
            docAttrset = Set(docAttrs)
            docAttrset.intersection_update(attrset)
            score = 0.0
            for docAttr in docAttrset:
                (attr_type, attr_kw) = docAttr.split(':')
                if attr_type == 'item':
                    score = score + 1.0
                elif attr_type == 'regulation':
                    score = score + 1.0
                elif attr_type == 'question':
                    score = score + 1.0
                else:
                    pass
            scores[cand] = score

    def getCandidate(self, cands, idxs, attrs):
        idxNum = len(idxs)
        if idxNum == 0:
            return
        print 'debug: ' + idxs[0].encode('utf-8')
        set0 = Set(self._indexes[idxs[0]])
        for i in range(idxNum-1):
            set0.intersection_update(Set(self._indexes[idxs[i+1]]))

        scores = {}
        self.scoreDocAttr(set0, attrs, scores)
        # scoring based on overlap of attrs
        sorted_docIds = sorted(list(set0), cmp = lambda x, y :cmp(scores[x], scores[y]), reverse=False)
        for docId in sorted_docIds:
            print 'docId: ' + self._content[docId]['title'].encode('utf-8') + '\t' + str(scores[docId])
        pp.pprint(scores)


    def genAttrs(self, attrs, blocks):
        if 'item' in blocks:
            attrs.append('item:' + blocks['item'])
        if 'regulation' in blocks:
            attrs.append('regulation:' + blocks['regulation'])
        if 'question' in blocks:
            attrs.append('question:' + blocks['question'])

    def extractFeature(self, blocks, index, attrs):
        if 'domain' not in blocks:
            return False
        if (blocks['domain'] != 'gov') or ('gov' not in blocks):
            return False

        self.genIndex(index, blocks['gov'])

        self.genAttrs(attrs, blocks['gov'])
        return (index, attrs)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='build-index.py', usage='''
                ./build-index.py --d dicFile
                                 --i indexFile
                                 --c contentFile
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='../../data/test/name.dic',
                        help='dictionary file path')
    parser.add_argument('--i', type=str,
                        default='./gov-index',
                        help='index file')
    parser.add_argument('--c', type=str,
                        default='./gov_q',
                        help='content file')

    args = parser.parse_args()
    dic = DictManager()
    dic.load_dict(args.d)

    nlu = NLU(dic)
    nlu.setPreprocessor('govTitle')
    nlu.appendTagger(GreedyTagger())
    tagger = RuleTagger()
    tagger.loadRules('./gov-rule')
    nlu.appendTagger(tagger)
    
    nlu.appendRewriter(RemoveTokRewriter())

    semantic = SemanticBase()
    semantic.loadSemanticRules('./gov-semantics.json')

    indexes = {}
    docs = {}
    indexer = GovTitleExtracter()
    indexer.getIndexId(dic)
    indexer.loadIndex(args.i)
    indexer.loadContent(args.c)
    #pp.pprint(indexer._indexes)


    for line in sys.stdin.readlines():
        rawText = line.strip().decode('utf-8')
        anaList = []
        nlu.tagText(anaList, rawText, True)
        res = []
        blocks = {}
        semantic.extract(anaList, blocks, '')
        idxs = []
        attrs = []
        indexer.extractFeature(blocks, idxs, attrs)
        pp.pprint(idxs)
        cands = []
        indexer.getCandidate(cands, idxs, attrs)
        
