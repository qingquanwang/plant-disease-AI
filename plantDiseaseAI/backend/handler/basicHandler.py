# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *

import pprint

pp = pprint.PrettyPrinter(indent = 2)

# A basic Handler should be able to handle the interface of
#    the understanding 
#    the ACK reply
#    ask the question of state
#    handle the branch logic
#    reset the state

class BaseHandler(object):
    def __init__(self, params, modules):
        self._id = params['Name']
        self._out = []
        self._dep = []
        for v in params['Out']:
            self._out.append(v)
        for v in params['Dependent']:
            self._dep.append(v)
    def accepted(self, state):
        pass
    def execute(self, state, userInput, actions):
        pass

class BaseQAHandler(BaseHandler):
    # params is the spec of the handler
    def __init__(self, params, modules):
        super(self, params, modules)
        # set NLU module
        nluName = params['nlu']
        if nluName in modules:
            self._nlu = modules[nluName]
        else:
            self._nlu = None
        # set NLR module
        nlrName = params['nlr']
        if nlrName in modules:
            self._nlr = modules[nlrName]
        else:
            self._nlr = None

class WelcomeHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(self, params, modules)
        self._welcomeMsgTemplateId = params['msg']['welcomeTemplateId']
    # Welcome Handler Always Accepted
    def accepted(self, state):
        return True

    # Output: 'taskType', 'plantName', 'diseaseName', 'intent'
    def understanding(self, state, text):
        anaList = self._nlu.analysis(text)
        # we only care for plantName, diseaseName, intent
        plantName = ''
        diseaseName = ''
        intent = ''
        for ana in anaList:
        # categorize the taskType
        if intent == '':
        elif plantName != '':
        elif diseaseName != '':
        else:
            
 
    # State Transition Graph:
    #   'Run' -> 'WaitTextInput' : reply welcomeMsg
    #   'WaitTextInput' -> 'Done' : reply ackMsg
    #   'Run' -> 'Repeat' -> 'WaitTextInput': reply repeatMsg
   
    def execute(self, state, userInput, actions):
        if state._state == 'Run':
            welcomeAction = Action('ShowPlainText')
            welcomeAction.setText(self._nlr.use_template(
                    self._welcomeMsgTemplateId,
                    state._session._env))
            actions.append(welcomeAction)
            state._state = 'WaitTextInput'
            return True
        elif state._state == 'WaitTextInput':
            if userInput._type != 'Text':
                return False
            return True
        else
            return False
