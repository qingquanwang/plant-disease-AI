# -*- coding: utf-8 -*-
# filename: main.py
import sys
from os.path import realpath, join, dirname
print(join(dirname(realpath(__file__)), '../../'))
sys.path.insert(0, join(dirname(realpath(__file__)), '../../'))


import web
import traceback
from handle import Handle


urls = (
    '/wx', 'Handle',
    '/', 'index',
    '/stop', 'stop',
)
app = web.application(urls, globals())


class index:
    def GET(self):
        info = 'empty'
        # 测试cookie
        # cookie = web.cookies(count='-1')
        # info = 'cookie.count = {}'.format(cookie.count)
        # int_count = int(cookie.count) + 1
        # web.setcookie('count', str(int_count), 3600)
        return "Hello, world! info = {}".format(info)


class stop:
    def GET(self):
        app.stop()


if __name__ == '__main__':
    app.run()
