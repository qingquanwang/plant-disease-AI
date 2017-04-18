#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import requests
import json
import os.path as path
import datetime
from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString

class FlightInfo(object):
    def __init__(self):
        self.carrier = ''
        self.code = ''
        self.img = ''
        self.departure = ''
        self.departure_plan = ''
        self.arrival = ''
        self.arrival_plan = ''
        self.from_airport = ''
        self.to_airport = ''
        self.ontime_rate = ''
        self.status = ''
        self.url = ''
    def pp(self):
        print(self.__dict__)
    def __str__(self):
        return '\t'.join(self.__dict__.values())

class FlightManager(object):

    UNKNOWN_CITY = None
    airport_list = {}

    def __init__(self):
        self.init_airport_list()

    def init_airport_list(self):
        if len(FlightManager.airport_list) != 0:
            return
        file_path = path.join(path.dirname(path.realpath(__file__)), 'airportlist.json')
        with open(file_path, 'r') as f:
            FlightManager.airport_list = json.load(f).get('in')
        # print(FlightManager.airport_list)
        print('init airport_list, len = {}'.format(len(FlightManager.airport_list)))

    def get_airport_code(self, city):
        if city in FlightManager.airport_list:
            return FlightManager.airport_list[city]['airportCode']
        else:
            return FlightManager.UNKNOWN_CITY

    def get_flight(self, from_airport, to_airport, when):
        '''
        获取航班信息，when = '20170405'
        '''
        DOMAIN = 'http://www.variflight.com'
        # 获取SITE_ID
        # http://www.variflight.com/
        FLIGHT_URL_1 = 'http://www.variflight.com/'
        # 获取航班信息
        # http://www.variflight.com/flight/CAN-PVG.html?AE71649A58c77&fdate=20170421
        FLIGHT_URL_2 = 'http://www.variflight.com/flight/{}-{}.html?{}&fdate={}'

        # 获取site_id
        r = requests.get(FLIGHT_URL_1)
        source = r.text.encode(r.encoding)
        site_id = re.search('var SITE_ID.*\'(.*)\'', source).group(1)

        # 获取航班列表
        flight_list = []
        url = FLIGHT_URL_2.format(from_airport, to_airport, site_id, when)
        print(url)
        r = requests.get(url)
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')

        tags = soup.select('div.fly_list li')
        for li in tags:
            div = li.select_one('div.li_com')
            fi = FlightInfo()
            fi.carrier = div.select('span.w260 b a')[0].string.encode('utf-8')
            fi.code = div.select('span.w260 b a')[1].string.encode('utf-8')
            fi.img = DOMAIN + div.select_one('img').get('src')
            # .select('a[href]')
            fi.departure = ''
            fi.departure_plan = div.select_one('span[dplan]').string.strip().encode('utf-8')
            fi.arrival = ''
            fi.arrival_plan = div.select_one('span[aplan]').string.strip().encode('utf-8')
            fi.from_airport = div.select('span.w150')[2].string.encode('utf-8')
            fi.to_airport = div.select('span.w150')[5].string.encode('utf-8')
            if div.select('span.w150')[-2].select_one('img'):
                fi.ontime_rate = div.select('span.w150')[-2].select_one('img').get('src')
            else:
                fi.ontime_rate = ''
            fi.status = div.select('span.w150')[-1].string.encode('utf-8')
            fi.url = DOMAIN + li.select_one('a').get('href')
            flight_list.append(fi)
        return flight_list


if __name__ == '__main__':
    mgr = FlightManager()
    from_airport = mgr.get_airport_code(u'广州白云')
    to_airport = mgr.get_airport_code(u'上海')
    print(from_airport, to_airport)
    for fi in mgr.get_flight(from_airport, to_airport, '20170405'):
        # fi.pp()
        print(fi)
