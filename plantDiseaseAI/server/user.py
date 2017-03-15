#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import simplejson as json
import util
import fire

json_path = './user_profile/'
file_ext = '.json'


class UserInfo(object):

    def __init__(self, openid):
        fpath = os.path.join(json_path, openid + file_ext)
        if os.path.isfile(fpath):
            util.lstr('老用户openid: {}'.format(openid))
            with open(fpath) as f:
                self.json_obj = json.load(f)
                # 强制转成str
                self.json_obj['question'] = self.json_obj['question'].encode('utf-8')
        else:
            util.lstr('新用户openid: {}'.format(openid))
            self.json_obj = {}
            self.json_obj['question'] = '问题为空'
        self.fpath = fpath

    def save(self):
        json_str = json.dumps(self.json_obj, ensure_ascii=False, indent=4, sort_keys=True)
        util.luni(json_str)
        util.save_to_file(self.fpath, json_str.encode('utf-8'))


class UserProfile(object):

    def __init__(self, openid):
        self.openid = openid
        self._data = UserInfo(openid)

    def set_info(self, key, value):
        self._data.json_obj[key] = value
        self._data.save()

    def get_info(self, key):
        return self._data.json_obj[key]


if __name__ == '__main__':
    fire.Fire(UserProfile)
