#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os.path as path
import datetime
from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString

class WeatherInfo(object):
    def __init__(self):
        self.date = None
        self.txt = ''
        self.img_day = ''
        self.img_night = ''
        self.temp_high = ''
        self.temp_low = ''
        self.wind_dir = ''
        self.wind_str = ''

    def __str__(self):
        return '{}: {}, {}, {}, {}/{}, {}, {}'.format(
            self.date, self.txt.encode('utf-8'), self.img_day, self.img_night,
            self.temp_high.encode('utf-8'), self.temp_low.encode('utf-8'),
            self.wind_dir.encode('utf-8'), self.wind_str.encode('utf-8'))

class WeatherManager(object):

    # 城市：http://cj.weather.com.cn/support/Detail.aspx?id=51837fba1b35fe0f8411b6df
    REQUEST_FAILED = u'requesting api failed'
    UNKNOWN_CITY = u'unknown city'
    AMBIGUOUS_CITY = u'ambiguous city'
    WEATHER_RESULT_FORMAT = u'{}: 最高温度: {}, 最低温度: {}'

    city_list = {}

    def __init__(self):
        self.init_city_list()

    def init_city_list(self):
        if len(WeatherManager.city_list) != 0:
            return
        file_path = path.join(path.dirname(path.realpath(__file__)), 'cities2.txt')
        with open(file_path, 'r') as f:
            for line in f:
                words = line.strip().split(',')
                WeatherManager.city_list[words[1]] = words[0]
        print('init city_list, len = {}'.format(len(WeatherManager.city_list)))

    def get_city(self, city):
        if city in WeatherManager.city_list:
            return WeatherManager.city_list[city]
        else:
            return None

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
            wi.img_night = imgs[1].get('src')
            wi.temp_low = day_li.select('span.temperature')[0].string.replace('/', '')
            wi.temp_high = day_li.select('span.temperature')[1].string.replace('/', '')
            # print(wi)
            day_delta += 1
            weather_info_15d.append(wi)

        # 获取7天的天气描述、风力
        r = requests.get(WEATHER_URL_2.format(city))
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')
        tags = soup.select('div#7d li.skyid')
        today = datetime.date.today()
        index = 0
        for day_li in tags:
            wi = weather_info_15d[index]
            wi.txt = day_li.select('p.wea')[0].string
            wind_spans = day_li.select('p.win span')
            wi.wind_dir = wind_spans[0].get('title') + u'转' + wind_spans[1].get('title')
            wi.wind_str = day_li.select('p.win i')[0].string
            print(wi)
            index += 1

        # 获取8-15天的天气描述、风力
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
    mgr = WeatherManager()
    city_id = mgr.get_city('沈阳')
    print(city_id)
    print mgr.get_weather(city_id)
