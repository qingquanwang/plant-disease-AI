# -*- coding: utf-8 -*-
import re
import json
from collections import deque
import os,sys
import pprint

pp = pprint.PrettyPrinter(indent = 2)

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

class State(object):
    def __init__(self):
        self._taskPath = []
        self._taskQueue = deque([])
        self._curTask = ''
        self._session = WhiteBoard()
        self._status = ''
        self._focus = ''
    @property
    def status(self):
        return self._status
    @status.setter
    def status(self, value):
        print('status <- {} previous: {}'.format(value, self._status))
        self._status = value
    def setStartState(self, taskId):
        self._status = 'Run'
        self._curTask = taskId
    def debugMsg(self):
        print "State Info: "
        print "\t\t Task Path:" + '--'.join(self._taskPath)
        print "\t\t Task Queue:" + '--'.join(self._taskQueue)
        print "\t\t Current Task:" + self._curTask
        print "\t\t session:" + self._session.serialize().encode('utf-8')
        print "\t\t status: " + self._status
        print "\t\t focus: " + self._focus
    def to_str(self):
        json_obj = {}
        json_obj['_taskPath'] = self._taskPath
        json_obj['_taskQueue'] = list(self._taskQueue)
        json_obj['_curTask'] = self._curTask
        json_obj['_session'] = self._session._env
        json_obj['_status'] = self._status
        json_obj['_focus'] = self._focus
        return json.dumps(json_obj)
    def from_str(self, json_str):
        json_obj = json.loads(json_str)
        self._taskPath = json_obj['_taskPath']
        self._taskQueue = deque(json_obj['_taskQueue'])
        self._curTask = json_obj['_curTask']
        self._session = WhiteBoard()
        self._session._env = json_obj['_session']
        self._status = json_obj['_status']
        self._focus = json_obj['_focus']

class UserInput(object):
    def __init__(self, inputType, inputContent):
        self._type = inputType
        self._input = inputContent
        # keep the analysis result during task transition
        self._ctx = {}
    def setContext(self, k, v):
        self._ctx[k] = v

class Action(object):
    def __init__(self, actionType):
        self._type = actionType
        self._text = '' #Dialog Reply or Questions
        self._contentApi = '' # Document api
    def setText(self, text):
        self._text = text
    def setContentApi(self, api):
        self._contentApi = api
    def debugMsg(self):
        print 'Action Info: [' + self._type + '] ' + self._text.encode('utf-8')
