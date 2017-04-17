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
import json

from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Dialog import *
from plantDiseaseAI.backend.Interaction import *
from plantDiseaseAI.backend.semantic import *


class Handle(object):

    dialog = None

    def __init__(self):
        if Handle.dialog is None:
            dic = DictManager()
            dic.load_dict('../../data/test/name.dic')
            nlu = NLU(dic)
            nlu.setPreprocessor('zhBook')
            nlu.appendTagger(GreedyTagger())
            tagger = RuleTagger()
            ruleFile = '../../data/test/RuleEngine/rule0'
            tagger.loadRules(ruleFile)
            nlu.appendTagger(tagger)

            nlr = NLR()
            nlr.load_template('../../data/reply-template')

            semantic = SemanticBase()
            semantic.loadSemanticRules('../../data/test/Semantics/wx-test-semantics.json')

            dialog = DialogManager()
            dialog.addModule("NLU", nlu)
            dialog.addModule("NLR", nlr)
            dialog.addModule("SEMANTIC", semantic)
            dialog.loadHandler('../../data/state-def-wx.json')
            Handle.dialog = dialog
        else:
            print('dialog already inited')

    def DoAction(self, actions, toUser, fromUser):
        ret = ''
        if not actions:
            ret = 'no action'
        elif len(actions) > 1:
            ret = 'too many actions'
        else:
            # actions[0].debugMsg()
            if actions[0]._type == 'ShowPlainText':
                ret = actions[0]._text.encode('utf-8')
            elif actions[0]._type == 'ShowNewsText':
                articles = []
                objs = json.loads(actions[0]._text)
                for obj in objs:
                    articles.append(reply.Article(**obj))
                replyMsg = reply.NewsMsg(toUser, fromUser, len(articles), articles)
                return replyMsg
        return reply.TextMsg(toUser, fromUser, ret)

    def HandleUserMsg(self, usr, recMsg, dialog, toUser, fromUser):
        state = State()
        state.from_str(usr.get_info('state'))
        state.debugMsg()
        userInput = UserInput('Text', recMsg.Content)
        actions = []
        dialog.execute(state, userInput, actions)
        state.debugMsg()
        usr.set_info('state', state.to_str())
        replyMsg = self.DoAction(actions, toUser, fromUser)
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
                    return self.HandleUserMsg(usr, recMsg, Handle.dialog, toUser, fromUser)
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
                        return self.HandleUserMsg(usr, recMsg, Handle.dialog, toUser, fromUser)
                else:
                    return reply.Msg().send()
            else:
                util.lstr("暂且不处理")
                return reply.Msg().send()
        except Exception, Argment:
            util.lstr('========Exception=======')
            util.lstr(traceback.format_exc())
            return Argment
