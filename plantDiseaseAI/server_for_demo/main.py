# -*- coding: utf-8 -*-
# filename: main.py
import web
import hashlib
import receive
import reply
import json
from media import Media

import util


urls = (
    '/wx', 'FakeHandle',
    '/', 'index',
    '/stop', 'stop',
)
app = web.application(urls, globals())


class FakeHandle:

    def process_txt(self, txt):
        txt = txt.decode('utf-8')
        print(txt)
        with open('pattern.json', 'r') as f:
            pattern_obj = json.load(f)
        print(pattern_obj)
        if txt in pattern_obj:
            return pattern_obj[txt]
        else:
            return u'unexpected input'

    def GET(self):
        try:
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "xiaogumsm"  # 请按照公众平台官网\基本配置中信息填写

            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            print "handle/GET func: hashcode, signature: ", hashcode, signature
            if hashcode == signature:
                return echostr
            else:
                return ""
        except Exception, Argument:
            return Argument

    def POST(self):
        webData = web.data()
        util.lstr("Handle Post webdata is: ")
        util.lstr(webData)
        # print(type(webData))  # str
        recMsg = receive.parse_xml(webData)
        if isinstance(recMsg, receive.Msg):
            toUser = recMsg.FromUserName
            fromUser = recMsg.ToUserName
            if recMsg.MsgType == 'text':
                # info = 'empty'
                # content = '收到问题: ' + recMsg.Content + ' info: ' + info
                content = self.process_txt(recMsg.Content)
                replyMsg = reply.TextMsg(toUser, fromUser, content.encode('utf-8'))
                return replyMsg.send()
            if recMsg.MsgType == 'image':
                # 发送信息
                # content = self.process_txt('image')
                # replyMsg = reply.TextMsg(toUser, fromUser, content.encode('utf-8'))
                # return replyMsg.send()
                replyMsg = reply.NewsMsg(toUser, fromUser, 1, '这可能是苹果白粉病', '苹果白粉病（Apple powdery mildew）在我国苹果产区发生普遍。除为害苹果外，还为害梨、沙果、海棠、槟子和山定子等，对山定子实生苗、小苹果类的槟沙果、海棠和苹果中的倭锦、祝、红玉、国光等品种为害重。', 'http://g.hiphotos.baidu.com/baike/w%3D268%3Bg%3D0/sign=442e0372f2d3572c66e29bdab228041a/18d8bc3eb13533facc74c7b5a8d3fd1f40345b6e.jpg', 'http://baike.baidu.com/item/%E8%8B%B9%E6%9E%9C%E7%99%BD%E7%B2%89%E7%97%85/10248498?fr=aladdin')
                return replyMsg.send()
            if recMsg.MsgType == 'voice':
                content = '用户: ' + recMsg.FromUserName + ' 发送了语音，转化为文字为: ' + recMsg.Recognition
                replyMsg = reply.TextMsg(toUser, fromUser, content)
                return replyMsg.send()
            else:
                return reply.Msg().send()
        else:
            util.lstr("暂且不处理")
            return reply.Msg().send()


class index:
    def GET(self):
        return "Hello, there!"


class stop:
    def GET(self):
        app.stop()


if __name__ == '__main__':
    app.run()
