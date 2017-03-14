# -*- coding: utf-8 -*-

class Index(object):
    def __init__(self, indexType, indexKW, sensitivity):
        self._indexType = indexType
        self._indexKW = indexKW
        self._sensitivity = sensitivity
    def serialize():
        return self._indexType + '|' + self._indexKW


class Plant(object):
    def __init(self, plantName):
        self._plantName = plantName
        self._alias = []
    def appendAlias(self, alias):
        self._alias.append(alias)

class Disease(object):
    def __init(self, disease):
        self.
