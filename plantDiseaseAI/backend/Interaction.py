# -*- coding: utf-8 -*-
import re
import json

class WhiteBoard(object):
    def __init__(self):
        # key:string <-> list(value:string)
        self._env = {}
    def append(self, k, v):
        if k not in self._env:
            self._env[k] = []
        if v not in self._env[k]:
            self._env[k].append(v)

    def override(self, k, v):
        if k not in self._env:
            self._env[k] = []
            self._env[k].append(v)
        else:
            self._env[k][0] = v

    # k1:v1,v2|k2:v3
    def serialize(self):
        res = []
        for k in self._env:
            res.append(k + ':' + ','.join(self._env[k]))
        return '|'.join(res)

    def deserialize(self, wp):
        if wp is None or wp == '':
            return
        for kv in wp.split('|'):
            k, values = kv.split(':')
            self._env[k] = values.split(',')

class Task(object):
    def __init__(self, obj):
        self._id = obj['Name']
        self._out = []
        self._dep = []
        for v in obj['Out']:
            self._out.append(v)
        for v in obj['Dependent']:
            self._out.append(v)

class State(object):
    def __init__(self):
        self._taskPath = []
        self._curTask = ''
        self._session = WhiteBoard()
        self._status = ''
        self._focus = ''

class UserInput(object):
    def __init__(self, inputType, inputContent):
        self._type = inputType
        self._input = inputContent

class Action(object):
    def __init__(self, actionType):
        self._type = actionType
        self._text = '' #Dialog Reply or Questions
        self._contentApi = '' # Document api
    def setText(self, text):
        self._text = text
    def setContentApi(self, api):
        self._contentApi = api

