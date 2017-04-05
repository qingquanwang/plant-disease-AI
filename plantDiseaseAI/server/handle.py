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


class Handle(object):
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
                    info = 'empty'
                    # 设置 cookie
                    # cookie = web.cookies(count='-1')
                    # info = 'cookie.count = {}'.format(cookie.count)
                    # int_count = int(cookie.count) + 1
                    # web.setcookie('count', str(int_count), 3600)
                    # end 设置 cookie
                    info = '之前的问题是: ' + ','.join(usr.get_info(user.jkey_quetions))
                    usr.set_info(user.jkey_quetions, recMsg.Content)
                    content = '收到问题: ' + recMsg.Content + ' info: ' + info
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    return replyMsg.send()
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
                    content = 'welcome! 用户: ' + recMsg.FromUserName
                    replyMsg = reply.TextMsg(toUser, fromUser, content)
                    return replyMsg.send()
                else:
                    return reply.Msg().send()
            else:
                util.lstr("暂且不处理")
                return reply.Msg().send()
        except Exception, Argment:
            util.lstr('========Exception=======')
            util.lstr(traceback.format_exc())
            return Argment
