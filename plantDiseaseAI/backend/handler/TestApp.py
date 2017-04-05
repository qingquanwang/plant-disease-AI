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

    # Output: [Domain]
    def understanding(self, state, userInput):
        text = userInput._input
        env = state._session._env
        anaList = self._nlu.tagText(text, True)
        userInput.setContext('cur_nlu_result', anaList)
        for ana in anaList:
            bestSeq = ana.getBestSeq(0.5)
            if 'domain' in bestSeq._annotation:
                domain = bestSeq._annotation['domain']
                if domain in ['weather' 'flight']:
                    env['domain'] = domain
                    break
        if 'domain' in env:
            return True
        else:
            return False

    # State Transition Graph:
    #   'Run' -> 'WaitTextInput' : reply welcomeMsg
    #   'WaitTextInput' -> 'Done' : move on, no actions returned
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

class ConfirmHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(WeatherHandler, self).__init__(params, modules)
        self._questionTemplateId = params['msg']['questionTemplateId']
        self._repeatTemplateId = params['msg']['repeatTemplateId']
    
    def accepted(self, state):
        env = state._session
        if env['domain'] == 'weather':
            return True
        else:
            return False

    # Output: []
    def understanding(self, state, userInput):
        
        env = state._session._env
        focus = state._focus
        if focus == '':
            return True

        anaList = self._nlu.tagText(text, True)
        
        for ana in anaList:
            bestSeq = ana.getBestSeq(0.5)

    # State Transition Graph:
    #   'Run' -> 'Done': understand all, return content-action
    #   'Run' -> 'WaitTextInput' : understand part of dependents, shift focus, return ask-focus
    #   'WaitTextInput' -> 'WaitTextInput' : understand the confirm-focus, shift focus, return ask-focus
    #   'WaitTextInput' -> 'WaitTextInput': reply tipsMsg
    #   'WaitTextInput' -> 'Done': there is no more focus, return content-action

    def execute(self, state, userInput, actions):
        # 1) check needs running
        if state._status == 'Run':
            (status, focus) = self.understanding(state, userInput._input)
            if status and focus == '':
                contentAction = self.composeContentAction(state)
                state._status = 'Done'
            elif status:
                askDepAction = Action('ShowPlainText')
                askDepAction.setText(self._nlr.use_template(
                                self.composeAskTemplateId(state._focus),
                                state._session._env))
                actions.append(askDepAction)
            else:
                tipsAction = Action('ShowPlainText')
                askDepAction.setText(self._nlr.use_template(
                                self._tipsMsgTemplateId,
                                state._session._env))
                actions.append(askDepAction)

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

class FlightHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(WeatherHandler, self).__init__(params, modules)
        self._tipsMsgTemplateId = params['msg']['tipsTemplateId']
    # Welcome Handler Always Accepted
    def accepted(self, state):
        return False
        env = state._session
        if env['domain'] == 'flight':
            return True
        else:
            return False

    # State Transition Graph:
    #   'Run' -> 'Done': understand all, return content-action
    #   'Run' -> 'WaitTextInput' : understand part of dependents, shift focus, return ask-focus
    #   'WaitTextInput' -> 'WaitTextInput' : understand the confirm-focus, shift focus, return ask-focus
    #   'WaitTextInput' -> 'WaitTextInput': reply tipsMsg
    #   'WaitTextInput' -> 'Done': there is no more focus, return content-action

    def execute(self, state, userInput, actions):
        return False
