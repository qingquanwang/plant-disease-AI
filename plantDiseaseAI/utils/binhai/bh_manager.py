#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json
import os.path as path
import datetime
from bs4 import BeautifulSoup
from bs4 import Tag
from bs4 import NavigableString

class BDBInfo(object):
    def __init__(self, url, titl, desc):
        self.url = ''
        self.title = ''
        self.desc = ''

# http://tj.bendibao.com/live/2017317/79538.shtm
ABSOLUTE_PREFIX = 'http://tj.bendibao.com/'

class BHManager(object):

    def __init__(self):
        pass

    def fetch_live_content(self, url):
        '''
        抓取天津本地宝的页面，支持相对路径、绝对路径
        '''
        if not url.startswith(ABSOLUTE_PREFIX):
            url = ABSOLUTE_PREFIX + url
        r = requests.get(url)
        source = r.text.encode(r.encoding)
        soup = BeautifulSoup(source, 'lxml')
        content_tag = soup.select_one('div.content_l')
        title = content_tag.select_one('h1 strong').string
        desc = content_tag.select_one('div.leading p').contents[1].string
        return url, title, desc

if __name__ == '__main__':
    mgr = BHManager()
    url = 'http://tj.bendibao.com/live/2017317/79538.shtm'
    url = 'live/20151221/75414.shtm'
    print(','.join(mgr.fetch_live_content(url)))