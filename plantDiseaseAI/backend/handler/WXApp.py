# -*- coding: utf-8 -*-
import re
import json
from collections import defaultdict
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.handler.basicHandler import *


class ChoiceHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(ChoiceHandler, self).__init__(params, modules)
        self._template = params['Template']
        self._name = params['Name']
        self._params = params
    def accepted(self, state):
        env = state._session._env
        if 'domain' in env['nlu'] and self._name == env['nlu']['domain']:
            return True
        else:
            return False
    def execute(self, state, userInput, actions):
        with open(self._template, 'r') as f:
            template = json.load(f)
            # print(json_obj
        env = state._session._env
        if 'history' not in env:
            env['history'] = []
        print (env)
        nextQID = self._params['StartQID']
        curQID = env['curQID'] if 'curQID' in env else self._params['StartQID']
        # find nextQID and set answer history
        if state._status == 'WaitTextInput':
            if userInput._input == self._params['ResetKey']:
                # 重置
                del env['history'][:]
            elif userInput._input == self._params['UnDoKey']:
                # 返回上一题
                if env['history'] and len(env['history']) > 0:
                    nextQID = env['history'].pop()
            else:
                # 功能按键之外的输入
                if curQID in template:
                    if userInput._input in template[curQID]['choices']:
                        # 回答有效 记录到答题历史
                        nextQID = template[curQID]['choices'][userInput._input]['goto']
                        env['history'].append(curQID)
                    else:  # 回答无效
                        nextQID = curQID
        else:
            # 初次答题
            state._status = 'WaitTextInput'
        # 显示题目及选项
        print('nextQID = ' + nextQID)
        env['curQID'] = nextQID
        reply = ''
        if 'choices' in template[nextQID]:
            # 显示选项
            reply += template[nextQID]['qst'] + ': \n'
            # print(template[nextQID]['choices'])
            for k, v in template[nextQID]['choices'].iteritems():
                reply += k + '. ' + v['display'] + '\n'
        else:
            # 答题结束
            reply += template[nextQID]['qst'] + ': \n'
            env['history'].append(curQID)
            state._status = 'Done'
        action = Action('ShowPlainText')
        action.setText(reply)
        actions.append(action)
        return True

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
        env = state._session._env
        if 'domain' in env['nlu'] and 'weather' == env['nlu']['domain']:
            return True
        else:
            return False
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
        self._params = params
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
                if 'domain' in jsonObj and jsonObj['domain'] in self._params['Out']:
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
