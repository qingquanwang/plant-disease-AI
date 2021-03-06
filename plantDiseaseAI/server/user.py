#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from os.path import realpath, join, dirname
import simplejson as json
import util
import fire
from collections import deque
from plantDiseaseAI.backend.Interaction import *

json_path = join(dirname(realpath(__file__)), './user_profile/')
file_ext = '.json'
max_history_length = 5

jkey_images = 'images'
jkey_quetions = 'questions'
jkey_version = 'version'

# 当前json格式版本，如果不同说明结构变化，当作新用户处理
CURRENT_VERSION = '1.0'


class UserInfo(object):
    def __init__(self, openid):
        fpath = join(json_path, openid + file_ext)
        self.fpath = fpath
        if os.path.isfile(fpath):
            util.lstr('老用户openid: {}'.format(openid))
            with open(fpath) as f:
                self.json_obj = json.load(f)
                if jkey_version in self.json_obj and self.json_obj[jkey_version] == CURRENT_VERSION:
                    questions = list(q for q in self.json_obj[jkey_quetions])
                    self.json_obj[jkey_quetions] = deque(questions, maxlen=max_history_length)
                    images = list(img for img in self.json_obj[jkey_images])
                    self.json_obj[jkey_images] = deque(images, maxlen=max_history_length)
                    return
                else:
                    util.lstr('老用户json格式不是最新，重新生成')

        util.lstr('新用户openid: {}'.format(openid))
        self.json_obj = {}
        self.json_obj[jkey_images] = deque([], maxlen=max_history_length)
        self.json_obj[jkey_quetions] = deque([], maxlen=max_history_length)
        self.reset_state()
        self.json_obj[jkey_version] = CURRENT_VERSION

    def reset_state(self, status='Run'):
        session = WhiteBoard()
        session.deserialize('')
        state = State()
        state.setStartState('Welcome')
        state._status = status
        state._session = session
        self.json_obj['state'] = state.to_str()

    def save(self):
        self.json_obj[jkey_quetions] = list(self.json_obj[jkey_quetions])
        self.json_obj[jkey_images] = list(self.json_obj[jkey_images])
        json_str = json.dumps(self.json_obj, ensure_ascii=False, indent=4, sort_keys=True)
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

    def reset(self):
        self._data.reset_state('WaitTextInput')
        self._data.save()

    def delete(self):
        self._data.delete()


if __name__ == '__main__':
    fire.Fire(UserProfile)
