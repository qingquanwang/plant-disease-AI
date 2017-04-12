#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

# 天气：https://free-api.heweather.com/v5/weather?city=闵行&key=5f5cbc0222bf49709c1c7f14d7016702
# 城市：https://api.heweather.com/v5/search?city=浦东&key=5f5cbc0222bf49709c1c7f14d7016702
SECRET = '5f5cbc0222bf49709c1c7f14d7016702'
WEATHER_URL = 'https://free-api.heweather.com/v5/weather?city={}&key=' + SECRET
CITY_URL = 'https://api.heweather.com/v5/search?city={}&key=' + SECRET
REQUEST_FAILED = u'requesting api failed'
UNKNOWN_CITY = u'unknown city'
AMBIGUOUS_CITY = u'ambiguous city'
WEATHER_RESULT_FORMAT = u'{}: 最高温度: {}, 最低温度: {}'
# CITY_RESULT_FORMAT = u'{}: 最高温度: {}, 最低温度: {}'

def get_city(city):
    r = requests.get(CITY_URL.format(city))
    if r.status_code == requests.codes.ok:
        return parse_city(r.text)
    else:
        return REQUEST_FAILED


def parse_city(json_str):
    if UNKNOWN_CITY in  json_str:
        return UNKNOWN_CITY
    json_obj = json.loads(json_str)
    return json_obj['HeWeather5']


def get_weather(city):
    r = requests.get(WEATHER_URL.format(city))
    if r.status_code == requests.codes.ok:
        return parse_weather(r.text)
    else:
        return REQUEST_FAILED


def parse_weather(json_str):
    if UNKNOWN_CITY in  json_str:
        return UNKNOWN_CITY
    json_obj = json.loads(json_str)
    if len(json_obj['HeWeather5']) != 1:
        return AMBIGUOUS_CITY
    result = []
    for daily in json_obj['HeWeather5'][0]['daily_forecast']:
        result.append(WEATHER_RESULT_FORMAT.format(daily['date'], daily['tmp']['max'], daily['tmp']['min']))
    return u','.join(result)


if __name__ == '__main__':
    print(get_weather('沈阳'))
    print(get_city('长宁'))
