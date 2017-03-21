# -*- coding: utf-8 -*-
from PlantDiseaseAI.backend.Tagging import *
from PlantDiseaseAI.backend.nlu import *
from PlantDiseaseAI.backend.nlr import *
from PlantDiseaseAI.backend.Interaction import *
from PlantDiseaseAI.backend.handler.basicHandler import *

import re
import json

class DialogManager(object):
    def __init__(self, filepath):
        self._variables = []
        self._tasks = {}
        # name -> module object
        self._modules = {}
        with open(filepath, 'r') as fd:
            taskDef = json.load(fd, encoding='utf-8')
            for variable in taskDef['WhiteBoard']:
                self._variables.append(variable)
            for taskObj in taskDef['Tasks']:
                task = Task(Obj)
                self._tasks[task._id] = task

    def loadHandler(self):
        

    def addModule(self, name, module):
        self._modules[name] = module

    def execute(self, state, userInput, actions):
        #1. check the current state
        if state._status == '':
            # start state
            pass
        elif state._state == 'WaitTextInput':
            # wait for user text input, we check user's input
            pass
        elif state._state == 'WaitImageInput':
            # wait for user image input, we check user's input
            pass
        else:
            pass#

        #2. understand userInput
        
        #3. state transition
        #4. return actions

