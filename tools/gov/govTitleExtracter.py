# -*- coding: utf-8 -*-
import pprint
import math
from sets import Set
import os,sys

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
        if 'org' in blocks and blocks['org'] in self._org2id:
            index.append('org:' + self._org2id[blocks['org']])
        if 'role' in blocks and (blocks['role'] in self._role2id):
            index.append('role:' + self._role2id[blocks['role']])
        if 'service' in blocks:
            index.append('service:' + blocks['service'])
        if 'condition' in blocks:
            index.append('condition:' + blocks['condition'])


    def genAttrs(self, attrs, blocks):
        if 'role' in blocks and (blocks['role'] in self._role2id):
            attrs.append('role:' + self._role2id[blocks['role']])
        if 'service' in blocks:
            attrs.append('service:' + blocks['service'])
        if 'condition' in blocks:
            attrs.append('condition:' + blocks['condition'])
        if 'item' in blocks:
            attrs.append('item:' + blocks['item'])
        if 'regulation' in blocks:
            attrs.append('regulation:' + blocks['regulation'])
        if 'question' in blocks:
            attrs.append('question:' + blocks['question'])

    def scoreDocAttr(self, candset, attrs, scores):
        attrWeight = {
            'item' : 1.0,
            'service' : 2.0,
            'question' : 2.0,
            'condition' : 4.0,
            'role' : 3.0,
            'regulation' : 4.0
        }
        attrset = Set(attrs)
        sum1 = 0.1
        for attr in attrset:
            attr_type = attr.split(':')[0]
            sum1 = sum1 + attrWeight[attr_type]

        for cand in candset:
            docAttrs = self._docAttrs[cand]
            docAttrset = Set(docAttrs)
            overlappedAttrSet =docAttrset.intersection(attrset)
            score = 0.1
            for docAttr in overlappedAttrSet:
                attr_type = docAttr.split(':')[0]
                score = score + attrWeight[attr_type]
            sum2 = 0.1
            for attr in docAttrset:
                attr_type = attr.split(':')[0]
        
                sum2 = sum2 + attrWeight[attr_type]
            score = score/math.sqrt(sum1 * sum2) + 5.0 / len(self._content[cand]['title'])
            scores[cand] = score

    def getCandidate(self, cands, idxs, attrs):
        idxNum = len(idxs)
        if idxNum == 0:
            return

        set0 = None
        if idxs[0] in self._indexes:
            set0 = Set(self._indexes[idxs[0]])
        else:
            return
        for i in range(idxNum-1):
            if idxs[i+1] in self._indexes:
                set1 = set0.intersection(Set(self._indexes[idxs[i+1]]))
                if len(set1) != 0:
                    set0 = set1

        scores = {}
        self.scoreDocAttr(set0, attrs, scores)
        # scoring based on overlap of attrs
        sorted_docIds = sorted(list(set0), cmp = lambda x, y :cmp(scores[x], scores[y]), reverse=True)
        maxDoc = 5
        for docId in sorted_docIds:
            cands.append(docId)
            maxDoc = maxDoc - 1
            if maxDoc == 0:
                break
        #pp.pprint(scores)

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
                    attrs = []
                    if value != '':
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


    def extractFeature(self, blocks, index, attrs):
        if 'domain' not in blocks:
            return False
        if (blocks['domain'] != 'gov') or ('gov' not in blocks):
            return False

        self.genIndex(index, blocks['gov'])

        self.genAttrs(attrs, blocks['gov'])
        return (index, attrs)
