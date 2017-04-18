# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.handler.WXApp import *
from plantDiseaseAI.backend.handler.basicHandler import *
from plantDiseaseAI.utils.flight.flight_variflight import *


class GetFlightPlaceHandler(GetHandler):
    def __init__(self, params, modules):
        super(GetFlightPlaceHandler, self).__init__(params, modules)
    def accepted(self, state):
        if not super(GetFlightPlaceHandler, self).accepted(state):
            return not self.is_valid(state)
        return True
    def understanding(self, state, text):
        return super(GetFlightPlaceHandler, self).understanding(state, text)
    def execute(self, state, userInput, actions):
        return super(GetFlightPlaceHandler, self).execute(state, userInput, actions)
    def is_valid(self, state):
        env = state._session._env
        current_place = env[self._required]['name']
        mgr = FlightManager()
        result = mgr.get_airport_code(current_place)
        print(result)
        if result is not None:
            env = state._session._env
            env[self._required]['code'] = result
            return True
        return False
    def customize_hook(self, state, userInput, actions):
        print('GetFlightPlaceHandler.customize_hook')
        if self.is_valid(state):
            state._status = 'Done'
        else:
            action = Action('ShowPlainText')
            action.setText(u'{}不是有效的机场名字，请重新例如上海浦东，上海，上海虹桥'.format(userInput._input))
            actions.append(action)
        return

class GetFlightDateHandler(GetHandler):
    def __init__(self, params, modules):
        super(GetFlightDateHandler, self).__init__(params, modules)
    def accepted(self, state):
        if not super(GetFlightDateHandler, self).accepted(state):
            return not self.is_valid(state)
        return True
    def understanding(self, state, text):
        return super(GetFlightDateHandler, self).understanding(state, text)
    def execute(self, state, userInput, actions):
        return super(GetFlightDateHandler, self).execute(state, userInput, actions)
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
        valid_dates = [base + datetime.timedelta(days=x) for x in range(-15, 15)]
        if m_date in valid_dates:
            env = state._session._env
            env[self._required]['time'] = m_date.strftime('%Y%m%d')
            return True
        else:
            return False
    def customize_hook(self, state, userInput, actions):
        if self.is_valid(state):
            state._status = 'Done'
        else:
            action = Action('ShowPlainText')
            action.setText(u'只支持查询过去15天到未来15天内的天气')
            actions.append(action)
        return

class DisplayFlightHandler(BaseQAHandler):
    def __init__(self, params, modules):
        super(DisplayFlightHandler, self).__init__(params, modules)
        self._msgTemplateId = params['msg']['MsgTemplateId']
    def accepted(self, state):
        return True
    def execute(self, state, userInput, actions):
        env = state._session._env
        print(env)
        from_airport = env['from']['code']
        to_airport = env['to']['code']
        m_date = env['date']['time']
        mgr = FlightManager()
        flight_list = mgr.get_flight(from_airport, to_airport, m_date)
        result = []
        item0 = {}
        item0['title'] = '查询{}从{}到{}的航班 powered by Cogik'.format(m_date, env['from']['name'].encode('utf-8'), env['to']['name'].encode('utf-8'))
        item0['desc'] = ''
        item0['picurl'] = 'http://www.xiaogu-tech.com/img/wx/cogik-rect.png'
        item0['url'] = 'http://www.xiaogu-tech.com/'
        result.append(item0)
        index = 1
        for fi in flight_list:
            item1 = {}
            temp = '{} {}  {}  {}  {}'.format(fi.carrier, fi.code, fi.departure_plan, fi.arrival, fi.status)
            item1['title'] = temp
            item1['desc'] = ''
            item1['picurl'] = fi.img
            item1['url'] = fi.url
            result.append(item1)
            index += 1
            if index == 8:
                break
        json_str = json.dumps(result, ensure_ascii=False)
        action = Action('ShowNewsText')
        action.setText(json_str.decode('utf-8'))
        actions.append(action)
        state._status = 'Done'
        return True
