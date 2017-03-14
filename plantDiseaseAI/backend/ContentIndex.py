# -*- coding: utf-8 -*-
import os,sys
import json

# class of index
class Index(object):
    def __init__(self, indexType, indexKW, sensitivity):
        self._indexType = indexType
        self._indexKW = indexKW
        self._sensitivity = sensitivity
    def serialize():
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
        self._docText = docText
    # return the raw content
    def getDoc():
        if self._docText is not None:
            return self._docText
        else
            with open(self._docFile) as fd:
                return fd.read()
    # TODO: format the document as json or html
    def getDocFormated():
        return self.getDoc()

# A native implementation of inverse list
# methods:
#   insert, dumpIndex, dumpAll, load, lookUp, intersect
class ContentPool(object):
    def __init__(self, indexOnly = False):
        self._index = {}
        self._content = {}
        self._indexOnly = indexOnly
    def insertDoc(index, doc):
        k = index.serialize()
        if k in self._index:
            self._index[k].append(copy.copy(doc))
        else:
            self._index[k] = []
            self._index[k].append(copy.copy(doc))
        # load content and insert into _content
        if not self._indexOnly:
            self._content[doc._docId] = doc.getDoc()

    def loadIndex(indexFile):
        
    def loadContent(contentFile):
    def dumpIndex(indexFile):
        
    def dumpAll(indexFile, contentFile):
