# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.Tagging import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.handler.basicHandler import *
from plantDiseaseAI.backend.handler.PlantDiseaseApp import *
from plantDiseaseAI.backend.handler.WXApp import *

import re
import json

class Task(object):
    def __init__(self, obj, modules):
        self._id = obj['Name']
        self._out = []
        self._dep = []
        self._handler = None
        if 'Out' in obj:
            for v in obj['Out']:
                self._out.append(v)
        if 'Dependent' in obj:
            for v in obj['Dependent']:
                self._dep.append(v)
        self._handler = eval(obj['Handler'])(obj, modules)

class DialogManager(object):
    def __init__(self):
        self._variables = []
        self._tasks = {}
        # name -> module object
        self._modules = {}

    def loadHandler(self, filepath):
        with open(filepath, 'r') as fd:
            taskDef = json.load(fd, encoding='utf-8')
            for variable in taskDef['WhiteBoard']:
                self._variables.append(variable)
            for taskObj in taskDef['Tasks']:
                task = Task(taskObj, self._modules)
                self._tasks[task._id] = task

    def addModule(self, name, module):
        self._modules[name] = module

    def execute(self, state, userInput, actions):
        temp_input = userInput
        if state._status == 'END':
            return True

        loop = True
        while loop:
            res = self._tasks[state._curTask]._handler.execute(state, temp_input, actions)
            if len(actions) > 0:
                loop = False
            if res == False:
                state._status = 'FAILED'
                return False
            if state._status == 'Done':
                state._taskPath.append(state._curTask)
                # move to next task
                for t in self._tasks[state._curTask]._out:
                    if t not in state._taskPath:
                        state._taskQueue.append(t)
                if len(state._taskQueue) == 0:
                    state._status = 'END'
                    loop = False
                    break
                state._curTask = state._taskQueue.popleft()
                state._status = 'Run'
                temp_input = userInput
        return True
