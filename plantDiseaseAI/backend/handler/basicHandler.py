# -*- coding: utf-8 -*-
from nlu import *
from nlr import *
from Interaction import *
from SemanticTagging import *

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
    def accepted(self, state):
        pass
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

class WelcomeHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(WelcomeHandler, self).__init__(params, modules)
        self._welcomeMsgTemplateId = params['msg']['welcomeTemplateId']
        self._repeatMsgTemplateId = params['msg']['repeatTemplateId']
    # Welcome Handler Always Accepted
    def accepted(self, state):
        return True

    # Output: 'taskType', 'plantName', 'diseaseName', 'intent'
    def understanding(self, state, text):
        anaList = self._nlu.analysis(text)
        status = semantic_mainTask(anaList, state._session)
        return status
 
    # State Transition Graph:
    #   'Run' -> 'WaitTextInput' : reply welcomeMsg
    #   'WaitTextInput' -> 'Done' : reply ackMsg
    #   'WaitTextInput' -> 'Repeat' -> 'WaitTextInput': reply repeatMsg
   
    def execute(self, state, userInput, actions):
        if state._status == 'Run':
            welcomeAction = Action('ShowPlainText')
            welcomeAction.setText(self._nlr.use_template(
                    self._welcomeMsgTemplateId,
                    state._session._env))
            actions.append(welcomeAction)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            status = self.understanding(state, userInput._input)
            if status == False:
                repeatAction = Action('ShowPlainText')
                repeatAction.setText(self._nlr.use_template(
                    self._repeatMsgTemplateId,
                    state._session._env))
                actions.append(repeatAction)
                state._status = 'WaitTextInput'
            else:
                state._status = 'Done'
            return True
        elif state._status == 'Done':
            return True
        else:
            return False
