# -*- coding: utf-8 -*-
# filename: main.py
import web
from handle import Handle


urls = (
    '/wx', 'Handle',
    '/', 'index',
    '/stop', 'stop',
)
app = web.application(urls, globals())


class index:
    def GET(self):
        return "Hello, worldd!"


class stop:
    def GET(self):
        app.stop()


if __name__ == '__main__':
    app.run()
