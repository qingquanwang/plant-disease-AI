# -*- coding: utf-8 -*-
from Tagging import *
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
    def searialize(self):
        res = []
        for k in self._env:
            res.append(k + ':' + ','.join(self._env[k]))
        return '|'.join(res)

    def desearialize(self, wp):
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

class DialogManager(object):
    def __init__(self, filepath):
        self._variables = []
        self._tasks = {}

        with open(filepath, 'r') as fd:
            taskDef = json.load(fd, encoding='utf-8')
            for variable in taskDef['WhiteBoard']:
                self._variables.append(variable)
            for taskObj in taskDef['Tasks']:
                task = Task(Obj)
                self._tasks[task._id] = task
    def execute_node(self, taskId, )
