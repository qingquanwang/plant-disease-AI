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
    def __init__(self, params):
        pass
    def accepted(self, state):
        pass
    def understanding(self, state, userInput):
        pass
    def state_transition(self, state):
        pass
    def generate_action(self, state, action):
        pass


class BaseQAHandler(BaseHandler):
    # params is the spec of the handler
    def __init__(self, params):
        self._id = params['Name']
        self._out = []
        self._dep = []
        for v in params['Out']:
            self._out.append(v)
        for v in params['Dependent']:
            self._dep.append(v)

    def accepted(self, state):
        pass
    def 

    
