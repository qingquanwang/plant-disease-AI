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


class UserInfo(object):
    def __init__(self, openid):
        fpath = join(json_path, openid + file_ext)
        if os.path.isfile(fpath):
            util.lstr('老用户openid: {}'.format(openid))
            with open(fpath) as f:
                self.json_obj = json.load(f)
                questions = list(q for q in self.json_obj[jkey_quetions])
                self.json_obj[jkey_quetions] = deque(questions, maxlen=max_history_length)
                images = list(img for img in self.json_obj[jkey_images])
                self.json_obj[jkey_images] = deque(images, maxlen=max_history_length)
                print(self.json_obj)
        else:
            util.lstr('新用户openid: {}'.format(openid))
            self.json_obj = {}
            self.json_obj[jkey_images] = deque([], maxlen=max_history_length)
            self.json_obj[jkey_quetions] = deque([], maxlen=max_history_length)
            self.reset_state()

        self.fpath = fpath

    def reset_state(self):
        session = WhiteBoard()
        session.deserialize('')
        state = State()
        state.setStartState('Welcome')
        state._session = session
        self.json_obj['state'] = state.to_str()

    def save(self):
        self.json_obj[jkey_quetions] = list(self.json_obj[jkey_quetions])
        self.json_obj[jkey_images] = list(self.json_obj[jkey_images])
        print(self.json_obj)
        json_str = json.dumps(self.json_obj, ensure_ascii=False, indent=4, sort_keys=True)
        print(json_str)
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
