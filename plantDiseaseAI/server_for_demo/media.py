# -*- coding: utf-8 -*-
# filename: media.py
from basic import Basic
import urllib2
import poster.encode
from poster.streaminghttp import register_openers
import hashlib
import os
import json


class Media(object):
    def __init__(self):
        register_openers()

    # 上传图片
    def upload(self, accessToken, filePath, mediaType):
        openFile = open(filePath, "rb")
        param = {'media': openFile}
        postData, postHeaders = poster.encode.multipart_encode(param)

        postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, mediaType)
        request = urllib2.Request(postUrl, postData, postHeaders)
        urlResp = urllib2.urlopen(request)
        print urlResp.read()

    def get(self, accessToken, mediaId):
        postUrl = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&media_id=%s" % (accessToken, mediaId)
        urlResp = urllib2.urlopen(postUrl)

        headers = urlResp.info().__dict__['headers']
        if ('Content-Type: application/json\r\n' in headers) or ('Content-Type: text/plain\r\n' in headers):
            jsonDict = json.loads(urlResp.read())
            print jsonDict
        else:
            buffer = urlResp.read()   # 素材的二进制
            mediaFile = file("test_media.jpg", "wb")
            mediaFile.write(buffer)
            print "get successful"

    def get_saved_url(self, url):
        m = hashlib.md5()
        m.update(url)
        md5 = m.hexdigest()
        print md5
        ext = '.png'
        if 'mmbiz_jpg' in url:
            ext = '.jpg'
        fileName = md5 + ext
        return 'http://123.206.178.188/static/' + fileName

    def save_user_image(self, url):
        postUrl = url
        urlResp = urllib2.urlopen(postUrl)

        headers = urlResp.info().__dict__['headers']
        if ('Content-Type: application/json\r\n' in headers) or ('Content-Type: text/plain\r\n' in headers):
            jsonDict = json.loads(urlResp.read())
            print jsonDict
        else:
            buffer = urlResp.read()  # 素材的二进制
            m = hashlib.md5()
            m.update(url)
            md5 = m.hexdigest()
            print md5
            ext = '.png'
            if 'mmbiz_jpg' in url:
                ext = '.jpg'
            fileName = md5 + ext
            mediaFile = file(fileName, "wb")
            mediaFile.write(buffer)
            os.rename(fileName, 'static/' + fileName)


if __name__ == '__main__':
    myMedia = Media()
    # accessToken = Basic().get_access_token()

    # filePath = "/root/msm/wechat_demo/files/xiaogu.png"   #请安实际填写
    # mediaType = "image"
    # myMedia.upload(accessToken, filePath, mediaType)

    # mediaId = "urOuD3rPtTprEt_meFddRX3GEc1FOGAKdzv3ArMFS_zEfLKK0jc3g8fig6Y7LOtS"
    # myMedia.get(accessToken, mediaId)

    imageUrl = "http://mmbiz.qpic.cn/mmbiz_jpg/RfIAqWf6EEYdibOyhB1aARia301DlmIsXia9YGhtILZ6utPx3UWXwvopf8IwuiaqbibgJb3yTtZGiaJmp1My0RJ6MCbw/0"
    print myMedia.save_user_image(imageUrl)
