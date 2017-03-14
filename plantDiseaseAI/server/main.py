# -*- coding: utf-8 -*-
# filename: main.py
import web
from handle import Handle


urls = (
    '/wx', 'Handle',
    '/', 'index'
)


class index:
    def GET(self):
        return "Hello, world!"


if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
