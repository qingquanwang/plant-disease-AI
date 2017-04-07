# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import reply
import receive
import web
import traceback
from media import Media
import user
import util
from DictManager import *
from nlu import *
from nlr import *
from Dialog import *
from Interaction import *


class Handle(object):

    def DoAction(self, actions):
        ret = ''
        if len(actions) != 1:
            ret = 'too many actions'
        elif actions[0]._type != 'ShowPlainText':
            ret = 'unexpected action'
        else:
            # actions[0].debugMsg()
            ret = actions[0]._text.encode('utf-8')
        return ret

    def HandleUserMsg(self, usr, recMsg, dialog, toUser, fromUser):
        state = State()
        state.from_str(usr.get_info('state'))
        state.debugMsg()
        userInput = UserInput('Text', recMsg.Content)
        actions = []
        dialog.execute(state, userInput, actions)
        state.debugMsg()
        usr.set_info('state', state.to_str())
        content = self.DoAction(actions)
        replyMsg = reply.TextMsg(toUser, fromUser, content)
        if state._status == 'END':
            usr.reset()
        return replyMsg.send()

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
        try:
            dic = DictManager()
            dic.load_dict('./data/test/name.dic')
            nlu = NLU(dic)
            nlu.setPreprocessor('zhBook')
            nlu.appendTagger(GreedyTagger())
            tagger = RuleTagger()
            ruleFile = './data/test/RuleEngine/rule0'
            tagger.loadRules(ruleFile)
            nlu.appendTagger(tagger)

            nlr = NLR()
            nlr.load_template('./data/reply-template')
            dialog = DialogManager()
            dialog.addModule("NLU", nlu)
            dialog.addModule("NLR", nlr)
            dialog.loadHandler('./data/state-def-wx.json')

            webData = web.data()
            util.lstr("Handle Post webdata is: ")
            util.lstr(webData)
            # print(type(webData))  # str
            recMsg = receive.parse_xml(webData)
            if isinstance(recMsg, receive.Msg):
                toUser = recMsg.FromUserName
                fromUser = recMsg.ToUserName
                usr = user.UserProfile(recMsg.FromUserName)
                if recMsg.MsgType == 'text':
                    return self.HandleUserMsg(usr, recMsg, dialog, toUser, fromUser)
                elif recMsg.MsgType == 'image':
                    # 保存图片
                    myMedia = Media()
                    imageUrl = recMsg.PicUrl
                    savedUrl = myMedia.get_saved_url(imageUrl)
                    myMedia.save_user_image(imageUrl)
                    # 发送信息
                    content = '用户: ' + recMsg.FromUserName + ' 发送图片，已保存在: ' + savedUrl
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    return replyMsg.send()
                    # mediaId = recMsg.MediaId
                    # replyMsg = reply.ImageMsg(toUser, fromUser, mediaId)
                    # return replyMsg.send()
                elif recMsg.MsgType == 'voice':
                    content = '用户: ' + recMsg.FromUserName + ' 发送了语音，转化为文字为: ' + recMsg.Recognition
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    return replyMsg.send()
                elif recMsg.MsgType == 'event':
                    print(u'event received, recMsg.Content = ' + recMsg.Content)
                    if recMsg.Content == u'unsubscribe':
                        usr.delete()
                        reply.Msg().send()
                    elif recMsg.Content == u'subscribe':
                        return self.HandleUserMsg(usr, recMsg, dialog, toUser, fromUser)
                else:
                    return reply.Msg().send()
            else:
                util.lstr("暂且不处理")
                return reply.Msg().send()
        except Exception, Argment:
            util.lstr('========Exception=======')
            util.lstr(traceback.format_exc())
            return Argment
