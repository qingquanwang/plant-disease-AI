# -*- coding: utf-8 -*-
from os.path import realpath, join, dirname
import json
from collections import defaultdict
import datetime
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.handler.basicHandler import *
from plantDiseaseAI.utils.weather_china import *
from plantDiseaseAI.utils.common import *

class ChoiceHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(ChoiceHandler, self).__init__(params, modules)
        self._template = join(dirname(realpath(__file__)), '../../../' + params['Template'])
        self._name = params['Name']
        self._params = params
    def accepted(self, state):
        return self.has_domain(state)
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
        print(env)
        city_id = env['place']['id']
        m_date = env['date']['time']
        mgr = WeatherManager()
        weather_info_15d = mgr.get_weather(city_id)
        result = []
        item0 = {}
        item0['title'] = 'Cogik Weather'
        item0['desc'] = ''
        item0['img'] = 'http://www.xiaogu-tech.com/img/wx/cogik-rect.png'
        item0['click'] = 'http://www.xiaogu-tech.com/'
        result.append(item0)
        for wi in weather_info_15d:
            if wi.date.strftime('%Y-%m-%d') == m_date:
                item1 = {}
                temp = wi.date.strftime('%Y-%m-%d') + '\t' + date_to_weekday(wi.date) + '\n'
                temp += wi.temp_high.encode('utf-8') + '/' + wi.temp_low.encode('utf-8') + '\n'
                temp += wi.wind_dir.encode('utf-8') + '\t' + wi.wind_str.encode('utf-8') + '\n'
                item1['title'] = temp
                item1['desc'] = ''
                item1['img'] = wi.img_day
                item1['click'] = 'http://www.xiaogu-tech.com/'
                result.append(item1)
                break
        json_str = json.dumps(result)
        print(json_str)
        # infos = reply.split('|||')
        # result = u'未找到天气数据'
        # for info in infos:
        #     if m_date in info:
        #         result = info
        #         break
        action = Action('ShowNewsText')
        # reply = self._nlr.use_template(self._msgTemplateId, state._session._env)
        # reply = reply.format(u'date', u'where', u'晴 1~16度')
        action.setText(json_str)
        actions.append(action)
        state._status = 'Done'
        return True

class GetHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(GetHandler, self).__init__(params, modules)
        self._required = params['required']
        self._msgTemplateId = params['msg']['MsgTemplateId']
    def accepted(self, state):
        if self.has_property(state, self._required):
            env = state._session._env
            domain = env['domain']
            if self.understanding(state, env[domain][self._required]):
                return False
            else:
                return True
        else:
            return True
    def customize_hook(self, state, userInput, actions):
        state._status = 'Done'
        return
    def understanding(self, state, text):
        anaList = []
        blocks = {}
        self._nlu.tagText(anaList, text, True)
        self._semantic.extract(anaList, blocks, '')
        blockStr = json.dumps(blocks, encoding='utf-8')
        print('blockStr = ' + blockStr)
        if self._required in blocks:
            state._session._env.update(blocks)
            return True
        else:
            return False
    def execute(self, state, userInput, actions):
        env = state._session._env
        if state._status == 'Run':
            action = Action('ShowPlainText')
            action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
            actions.append(action)
            state._status = 'WaitTextInput'
            return True
        elif state._status == 'WaitTextInput':
            status = self.understanding(state, userInput._input)
            if status == False:
                action = Action('ShowPlainText')
                action.setText(self._nlr.use_template(self._msgTemplateId, state._session._env))
                actions.append(action)
                state._status = 'WaitTextInput'
            else:
                self.customize_hook(state, userInput, actions)
            return True
        else:
            return True

class OverallHandler(BaseQAHandler):
    '''
    确定domain后，根据用户的输入决定是否要显示tips，主要引导用户尽可能跳过之后一个个的GetHandler
    '''
    def __init__(self, params, modules):
        super(OverallHandler, self).__init__(params, modules)
        self._tipTemplateId = params['msg']['tipTemplateId']
    def accepted(self, state):
        return self.has_domain(state)
    def understanding(self, state, text):
        anaList = []
        blocks = {}
        self._nlu.tagText(anaList, text, True)
        self._semantic.extract(anaList, blocks, '')
        blockStr = json.dumps(blocks, encoding='utf-8')
        print('blockStr = ' + blockStr)
        state._session._env.update(blocks)
        return True
    def execute(self, state, userInput, actions):
        env = state._session._env
        if state._status == 'Run':
            if len(set(self._params['properties']).intersection(env[self._id])) == 0:
                action = Action('ShowPlainText')
                action.setText(self._nlr.use_template(
                    self._tipTemplateId,
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

class SelectDomainHandler(BaseQAHandler):
    '''
    作为起始Handler，引导用户确定domain
    '''
    def __init__(self, params, modules):
        super(SelectDomainHandler, self).__init__(params, modules)
        self._welcomeMsgTemplateId = params['msg']['welcomeTemplateId']
        self._repeatMsgTemplateId = params['msg']['repeatTemplateId']
    # Welcome Handler Always Accepted
    def accepted(self, state):
        return True

    # Output: 'taskType', 'plantName', 'diseaseName', 'intent'
    def understanding(self, state, text):
        anaList = []
        blocks = {}
        self._nlu.tagText(anaList, text, True)
        self._semantic.extract(anaList, blocks, '')
        blockStr = json.dumps(blocks, encoding='utf-8')
        print('blockStr = ' + blockStr)
        if 'domain' in blocks and blocks['domain'] in self._params['Out']:
            state._session._env = defaultdict(lambda:{}, blocks)
            state._session._env.update(blocks)
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

class GetPlaceHandler(GetHandler):
    def __init__(self, params, modules):
        super(GetPlaceHandler, self).__init__(params, modules)
    def accepted(self, state):
        if not super(GetPlaceHandler, self).accepted(state):
            return not self.is_valid(state)
        return True
    def understanding(self, state, text):
        return super(GetPlaceHandler, self).understanding(state, text)
    def execute(self, state, userInput, actions):
        return super(GetPlaceHandler, self).execute(state, userInput, actions)
    def is_valid(self, state):
        env = state._session._env
        current_place = env[self._required]['name']
        mgr = WeatherManager()
        result = mgr.get_city(current_place.encode('utf-8'))
        print(result)
        if result is not None:
            env = state._session._env
            env[self._required]['id'] = result
            return True
        return False
    def customize_hook(self, state, userInput, actions):
        if self.is_valid(state):
            state._status = 'Done'
        else:
            action = Action('ShowPlainText')
            action.setText(u'{}不在可查询范围里'.format(current_place))
            actions.append(action)
        return

class GetDateHandler(GetHandler):
    def __init__(self, params, modules):
        super(GetDateHandler, self).__init__(params, modules)
    def accepted(self, state):
        if not super(GetDateHandler, self).accepted(state):
            return not self.is_valid(state)
        return True
    def understanding(self, state, text):
        return super(GetDateHandler, self).understanding(state, text)
    def execute(self, state, userInput, actions):
        return super(GetDateHandler, self).execute(state, userInput, actions)
    def is_valid(self, state):
        env = state._session._env
        date_obj = env[self._required]
        if 'ymd' == date_obj['type']:
            if 'year' not in date_obj:
                date_obj['year'] = datetime.date.today().year
            m_date = datetime.datetime(int(date_obj['year']), int(date_obj['mon']), int(date_obj['day'])).date()
        elif 'today' == date_obj['type']:
            m_date = datetime.date.today()
        elif 'tomorrow' == date_obj['type']:
            m_date = datetime.date.today() + datetime.timedelta(days=1)
        print(m_date)
        base = datetime.date.today()
        valid_dates = [base + datetime.timedelta(days=x) for x in range(0, 15)]
        if m_date in valid_dates:
            env = state._session._env
            env[self._required]['time'] = m_date.strftime('%Y-%m-%d')
            return True
        else:
            return False
    def customize_hook(self, state, userInput, actions):
        if self.is_valid(state):
            state._status = 'Done'
        else:
            action = Action('ShowPlainText')
            action.setText(u'只支持查询15天内的天气')
            actions.append(action)
        return