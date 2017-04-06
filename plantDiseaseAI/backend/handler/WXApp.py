# -*- coding: utf-8 -*-
import re
import json
from collections import defaultdict
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.handler.basicHandler import *


class DisplayWeatherHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(DisplayWeatherHandler, self).__init__(params, modules)
        self._msgTemplateId = params['msg']['MsgTemplateId']
    def accepted(self, state):
        return True
    def execute(self, state, userInput, actions):
        env = state._session._env
        action = Action('ShowPlainText')
        date = ''.join(env['nlu']['slots']['date'])
        where = ''.join(env['nlu']['slots']['where'])
        print(u'{}{}{}'.format(date, where, u'晴 1~16度'))
        reply = self._nlr.use_template(self._msgTemplateId, state._session._env)
        reply = reply.format(date, where, u'晴 1~16度')
        action.setText(reply)
        actions.append(action)
        state._status = 'Done'
        return True


class GetHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(GetHandler, self).__init__(params, modules)
        self._required = params['misc']['required']
        self._msgTemplateId = params['msg']['MsgTemplateId']
    def accepted(self, state):
        return True
    def understanding(self, state, text):
        anaList = []
        self._nlu.tagText(anaList, text, True)
        for ana in anaList:
            analysis = ana.dumpBestSeq(True)
            print(analysis.encode('utf-8'))
            searchObj = re.search(r'{(.*)}', analysis.encode('utf-8'))
            if searchObj:
                jsonObj = json.loads(searchObj.group())
                if 'slots' in jsonObj:
                    print('slots in jsonObj')
                    env = state._session._env
                    env['nlu']['slots'].update(jsonObj['slots'])
                    return True
        return False
    def execute(self, state, userInput, actions):
        env = state._session._env
        if self._required in env['nlu']['slots']:
            print('required value: {} already found, skip'.format(self._required))
            state._status = 'Done'
            return True
        if state._status == 'Run':
            action = Action('ShowPlainText')
            action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
            actions.append(action)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            status = self.understanding(state, userInput._input)
            if status == False:
                print('understanding failed')
            if self._required not in env['nlu']['slots']:
                action = Action('ShowPlainText')
                action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
                actions.append(action)
                state._status = 'WaitTextInput'
            else:
                state._status = 'Done'
            return True
        else:
            return True

class WeatherHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(WeatherHandler, self).__init__(params, modules)
        self._welcomeMsgTemplateId = params['msg']['welcomeTemplateId']
    def accepted(self, state):
        return True
    def understanding(self, state, text):
        anaList = []
        self._nlu.tagText(anaList, text, True)
        for ana in anaList:
            analysis = ana.dumpBestSeq(True)
            print(analysis.encode('utf-8'))
            searchObj = re.search(r'{(.*)}', analysis.encode('utf-8'))
            if searchObj:
                jsonObj = json.loads(searchObj.group())
                if 'slots' in jsonObj:
                    print('slots in jsonObj')
                    env = state._session._env
                    env['nlu']['slots'].update(jsonObj['slots'])
                    return True
        return False
    def execute(self, state, userInput, actions):
        env = state._session._env
        print(env['nlu'])
        if state._status == 'Run':
            if 'where' not in env['nlu']['slots'] and 'date' not in env['nlu']['slots']:
                action = Action('ShowPlainText')
                action.setText(self._nlr.use_template(
                    self._welcomeMsgTemplateId,
                    state._session._env))
                actions.append(action)
                state._status = 'WaitTextInput'
                return True
            else:
                state._status = 'Done'
                return True
        elif state._status == 'WaitTextInput':
            state._status = 'Done'
            status = self.understanding(state, userInput._input)
            if status == False:
                print('understanding failed')
            return True
        else:
            return True

class WXHandler(BaseQAHandler):

    def __init__(self, params, modules):
        super(WXHandler, self).__init__(params, modules)
        self._welcomeMsgTemplateId = params['msg']['welcomeTemplateId']
        self._repeatMsgTemplateId = params['msg']['repeatTemplateId']
    # Welcome Handler Always Accepted
    def accepted(self, state):
        return True

    # Output: 'taskType', 'plantName', 'diseaseName', 'intent'
    def understanding(self, state, text):
        anaList = []
        self._nlu.tagText(anaList, text, True)
        for ana in anaList:
            analysis = ana.dumpBestSeq(True)
            print(analysis.encode('utf-8'))
            searchObj = re.search(r'{(.*)}', analysis.encode('utf-8'))
            if searchObj:
                # print "searchObj.group() : ", searchObj.group()
                jsonObj = json.loads(searchObj.group())
                if 'domain' in jsonObj and jsonObj['domain'] in ['weather', 'flight']:
                    env = state._session._env
                    env['nlu'] = defaultdict(lambda:{}, jsonObj)
                    return True
        return False

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
