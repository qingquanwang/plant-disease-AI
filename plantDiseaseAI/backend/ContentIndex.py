# -*- coding: utf-8 -*-
import os,sys
import json
import math

# class of index
class Index(object):
    def __init__(self, indexType, indexKW, sensitivity = 1.0):
        self._indexType = indexType
        self._indexKW = indexKW
        self._sensitivity = sensitivity
    def getKey():
        return self._indexType + '|' + self._indexKW

# all classes for document object
class Plant(object):
    def __init__(self, plantName):
        self._plantName = plantName
        self._alias = []
    def appendAlias(self, alias):
        self._alias.append(alias)

class Disease(object):
    def __init__(self, shortName):
        self._name = shortName
        self._alias = []
        self._effectedPlants = []

    def appendAlias(self, alias):
        self._alias.append(alias)

    # append the normalized name of plant
    def appendEffectedPlant(self, pnNormalized):
        self._effectedPlants.append(pnNormalized)

# class of each document
# docText must be Json formated!!
class ContentDoc(object):
    def __init__(docId, docType, docFile, docText = None):
        self._docId = docId
        self._docType = docType
        self._docFile = docFile
        if self._docFile == '':
            self._docFile = None
        self._docText = docText
        if self._docText == '':
            self._docText = None
    def dump():
        res = []
        res.append(self._docId)
        res.append(self._docType)
        if self._docFile is not None:
            res.append(self._docFile.encode('utf-8'))
        else:
            res.append('')
        if self._docText is not None:
            res.append(self._docText)
        else:
            res.append('')
        return '\t'.join(res)

    # return the json object
    def getDoc():
        if self._docText is not None:
            return json.loads(self._docText, encoding='utf-8')
        else
            if self._docFile is None:
                return None
            with open(self._docFile) as fd:
                return json.load(fd, encoding='utf-8')
    # TODO: format the document as json or html
    def getDocFormated():
        return self.getDoc()

# A native implementation of inverse list
# methods:
#   insert, dumpIndex, dumpAll, load, lookUp, intersect
class ContentPool(object):
    def __init__(self):
        # Index key -> list([docId, docType])
        self._index = {}
        # Index key -> idf
        self._idf = {}
        # docId -> doc object
        self._content = {}
    def insertDoc(self, index, doc):
        k = index.getKey()
        if k in self._index:
            self._index[k].append((doc._docId, doc._docType))
        else:
            self._index[k] = []
            self._idf[k] = index._sensitivity
            self._index[k].append((doc._docId, doc._docType))
        self._content[doc._docId] = copy.deepcopy(doc)

    # Format: type | KW  \t idf \t docId \002 docType \001 docId \002 docType ...
    def loadIndex(self, indexFile):
        with open(indexFile, 'r') as fd:
            for line in fd.readlines():
                key, idf, docList = line.strip('\n').split('\t')
                self._index[key] = []
                self._idf[key] = float(idf)
                for docs in docList.split('\001'):
                    (docId, docType) = docs.split('\002')
                    self._index[key].append((docId, docType))

    def dumpIndex(self, indexFile):
        with open(indexFile, 'w') as fd:
            for k in self._index:
                res = []
                res.append(k)
                res.append("%.4f" % (self._idf[k]))
                docList = []
                for docInfo in self._index[k]:
                    docList.append(docInfo[0] + '\002' + docInfo[1])
                res.append('\001'.join(docList))
                fd.write(('\t'.join(res)).encode('utf-8') + '\n')
    # Format: docId \t docType \t docPath \t docJson(one line,without \t \n)
    def loadContent(self, contentFile):
        with open(contentFile, 'r') as fd:
            for line in fd.readlines():
                docId, docType, docPath, docText = line.strip('\n').split('\t')
                doc = ContentDoc(docId, docType, docPath, docText)
                self._content[doc._docId] = copy.deepcopy(doc)

    def dumpContent(self, contentFile):
        with open(contentFile, 'w') as fd:
            for docId in self._content:
                doc = self._content[docId]
                fd.write(doc.dump() + '\n')
