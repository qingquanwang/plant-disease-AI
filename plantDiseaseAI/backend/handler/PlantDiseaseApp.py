# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.handler.basicHandler import *

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
        anaList = []
        self._nlu.tagText(anaList, text, True)
        ##TODO
        ####status = semantic_mainTask(anaList, state._session)
        env = state._session._env
        env['taskType'] = 'plant'
        env['plantName'] = 'apple'
        return True
 
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
