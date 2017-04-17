#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os.path as path
import datetime
from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString

class FlightInfo(object):
    def __init__(self):
        self.info = ''
        self.departure = ''
        self.departure_plan = ''
        self.arraival = ''
        self.arraival_plan = ''
        self.from_airport = ''
        self.to_airport = ''
        self.ontime_rate = ''
        self.status = ''

    def __str__(self):
        return '\t'.join(self.__dic__.values())

class FlightManager(object):

    airport_list = {}

    def __init__(self):
        self.init_airport_list()

    def init_airport_list(self):
        if len(FlightManager.airport_list) != 0:
            return
        file_path = path.join(path.dirname(path.realpath(__file__)), 'airportlist.json')
        with open(file_path, 'r') as f:
            FlightManager.airport_list = json.load(f).get('in')
        print('init airport_list, len = {}'.format(len(FlightManager.airport_list)))

    def get_airport_code(self, city):
        if city in FlightManager.airport_list:
            return FlightManager.city_list[city]
        else:
            return FlightManager.UNKNOWN_CITY

    def get_weather(self, city):
        # 获取15天天气的图片
        # http://m.weather.com.cn/mweather15d/101070101.shtml
        WEATHER_URL_1 = 'http://m.weather.com.cn/mweather15d/{}.shtml'
        # 获取7天的天气描述、风力
        # http://www.weather.com.cn/weather/101070101.shtml
        WEATHER_URL_2 = 'http://www.weather.com.cn/weather/{}.shtml'
        # 获取8-15天天气描述、风力
        # http://www.weather.com.cn/weather15d/101070101.shtml
        WEATHER_URL_3 = 'http://www.weather.com.cn/weather15d/{}.shtml'

        weather_info_15d = []
        # 获取15天天气的图片
        r = requests.get(WEATHER_URL_1.format(city))
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')
        tags = soup.select('li.ng-scope')
        today = datetime.date.today()
        day_delta = 0
        for day_li in tags:
            wi = WeatherInfo()
            wi.date = today + datetime.timedelta(days=day_delta)
            imgs = day_li.select('div img')
            wi.img_day = imgs[0].get('src')
            if len(imgs) > 1:
                wi.img_night = imgs[1].get('src')
            wi.temp_low = day_li.select('span.temperature')[0].string.replace('/', '')
            if len(day_li.select('span.temperature')) > 1:
                wi.temp_high = day_li.select('span.temperature')[1].string.replace('/', '')
            # print(wi)
            day_delta += 1
            weather_info_15d.append(wi)

        # 获取7天的天气描述、风力
        print('获取7天的天气描述、风力')
        r = requests.get(WEATHER_URL_2.format(city))
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')
        tags = soup.select_one('div#7d ul').select('li')
        today = datetime.date.today()
        index = 0
        for day_li in tags:
            wi = weather_info_15d[index]
            wi.txt = day_li.select('p.wea')[0].string
            wind_spans = day_li.select('p.win span')
            wi.wind_dir = wind_spans[0].get('title')
            if len(wind_spans) > 1:
                wi.wind_dir += u'转' + wind_spans[1].get('title')
            wi.wind_str = day_li.select('p.win i')[0].string
            print(wi)
            index += 1

        # 获取8-15天的天气描述、风力
        print('获取8-15天的天气描述、风力')
        r = requests.get(WEATHER_URL_3.format(city))
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')
        tags = soup.select('div#15d li')
        today = datetime.date.today()
        index = 7
        for day_li in tags:
            wi = weather_info_15d[index]
            wi.txt = day_li.select('span.wea')[0].string
            wi.wind_dir = day_li.select('span.wind')[0].string
            wi.wind_str = day_li.select('span.wind1')[0].string
            print(wi)
            index += 1

        return weather_info_15d


if __name__ == '__main__':
    mgr = FlightManager()
    city_id = mgr.get_city('无锡')
    print(city_id)
    print mgr.get_weather(city_id)
