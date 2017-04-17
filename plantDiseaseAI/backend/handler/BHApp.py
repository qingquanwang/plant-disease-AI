# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.handler.basicHandler import *
from plantDiseaseAI.utils.binhai.bh_manager import *


class DisplayBHHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(DisplayBHHandler, self).__init__(params, modules)
        self._msgTemplateId = params['msg']['tipsTemplateId']
    def accepted(self, state):
        return self.has_domain(state)
    def execute(self, state, userInput, actions):
        env = state._session._env
        if state._status == 'Run':
            action = Action('ShowPlainText')
            action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
            actions.append(action)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            state._status = 'Done'
            mgr = BHManager()
            url = 'live/20151221/75414.shtm'
            print(','.join(mgr.fetch_live_content(url)))
            return True
        else:
            return True