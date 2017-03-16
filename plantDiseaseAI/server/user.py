#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import simplejson as json
import util
import fire
from collections import deque

json_path = './user_profile/'
file_ext = '.json'
max_history_length = 5

jkey_images = 'images'
jkey_quetions = 'questions'


class UserInfo(object):

    def __init__(self, openid):
        fpath = os.path.join(json_path, openid + file_ext)
        if os.path.isfile(fpath):
            util.lstr('老用户openid: {}'.format(openid))
            with open(fpath) as f:
                self.json_obj = json.load(f)
                # 强制转成str
                questions = list(q.encode('utf-8') for q in self.json_obj[jkey_quetions])
                self.json_obj[jkey_quetions] = deque(questions, maxlen=max_history_length)
                images = list(img.encode('utf-8') for img in self.json_obj[jkey_images])
                self.json_obj[jkey_images] = deque(images, maxlen=max_history_length)
        else:
            util.lstr('新用户openid: {}'.format(openid))
            self.json_obj = {}
            self.json_obj[jkey_images] = deque([], maxlen=max_history_length)
            self.json_obj[jkey_quetions] = deque([], maxlen=max_history_length)
        self.fpath = fpath

    def save(self):
        self.json_obj[jkey_quetions] = list(self.json_obj[jkey_quetions])
        self.json_obj[jkey_images] = list(self.json_obj[jkey_images])
        json_str = json.dumps(self.json_obj, ensure_ascii=False, indent=4, sort_keys=True)
        util.luni(json_str)
        util.save_to_file(self.fpath, json_str.encode('utf-8'))

    def delete(self):
        try:
            os.remove(self.fpath)
        except OSError:
            pass


class UserProfile(object):

    def __init__(self, openid):
        self.openid = openid
        self._data = UserInfo(openid)

    def set_info(self, key, value):
        if isinstance(self._data.json_obj[key], deque):
            self._data.json_obj[key].append(value)
        else:
            self._data.json_obj[key] = value
        self._data.save()

    def get_info(self, key):
        return self._data.json_obj[key]

    def clear(self):
        self._data.delete()


if __name__ == '__main__':
    fire.Fire(UserProfile)
