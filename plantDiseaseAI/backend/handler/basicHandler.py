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
        self._params = params
    def accepted(self, state):
        pass
    def has_property(self, state, property):
        env = state._session._env
        domain = env['domain']
        if property in env[domain]:
            print('required property: {} already found, skip'.format(property))
            return True
        return False
    def has_domain(self, state, domain=None):
        env = state._session._env
        key = self._id
        if domain is not None:
            key = domain
        if key == env['domain']:
            return True
        else:
            return False
    def execute(self, state, userInput, actions):
        pass

class DummyTestHandler(BaseHandler):
    def __init__(self, params, modules):
        super(DummyTestHandler, self).__init__(params, modules)
    def accepted(self, state):
        return True
    # 'Run' -> 'WaitTextInput'
    # 'WaitTextInput' -> 'Ack': echo the input msg
    def execute(self, state, userInput, actions):
        if state._status == 'Run':
            action = Action('ShowPlainText')
            action.setText('Dummy Task [' + self._id + ']')
            actions.append(action)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            action = Action('ShowPlainText')
            action.setText('Got it! "' + userInput._input +'"')
            actions.append(action)
            state._status = 'Done'
            return True
        else:
            return True
class BaseQAHandler(BaseHandler):
    # params is the spec of the handler
    def __init__(self, params, modules):
        super(BaseQAHandler, self).__init__(params, modules)
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
        # set SEMANTIC modle
        semantic_name = 'SEMANTIC'
        if 'semantic' in params:
            semantic_name = params['semantic']
        self._semantic = modules[semantic_name]
    def execute(self, state, userInput, actions):
        pass