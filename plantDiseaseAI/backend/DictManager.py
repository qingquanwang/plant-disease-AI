# -*- coding: utf-8 -*-
import json
import re
import copy
import os
import sys
import pprint

pp = pprint.PrettyPrinter(indent=2)

class Entity(object):
    def __init__(self, t, idx):
        self._type = t
        self._id = idx

class DictManager(object):
    def __init__(self):
        self._names = {}
    def lookup(self, name):
        if name not in self._names:
            return []
        return self._names[name]
    # Format: name \t type \t id
    def load_dict(self, dict_file):
        with open(dict_file, 'r') as fd:
            for line in fd.readlines():
                (name, t, idx) = line.decode('utf-8').strip().split('\t')
                if name not in self._names:
                    self._names[name] = []
                e = Entity(t, idx)
                self._names[name].append(e)

    def compile_dict(self, dict_root, dict_file):
        for root, dirs, files in os.walk(dict_root):
            for name in files:
                file_path = os.path.join(root, name)
                sys.stderr.write("processing: " + file_path.encode('utf-8') + '\n')
                dic_type = '/'.join(file_path.replace(dict_root, '', 1).split('.')[:-1])
                sys.stderr.write("dic type: " + dic_type.encode('utf-8') + '\n')
                with open(file_path, 'r') as fd:
                    label = 0
                    for line in fd.readlines():
                        if line.startswith('#'):
                            continue
                        fs = line.decode('utf-8').strip().split('\t')
                        fieldNum = len(fs)
                        name = fs[0]
                        idx = ''
                        if fieldNum == 1:
                            idx = dic_type + '-' + str(label)
                            label = label + 1
                        else:
                            idx = fs[1]
                        if name not in self._names:
                            self._names[name] = []
                        self._names[name].append(Entity(dic_type, idx))
        with open(dict_file, 'w') as fd:
            for name in self._names:
                for e in self._names[name]:
                    res = []
                    res.append(name)
                    res.append(e._type)
                    res.append(e._id)
                    fd.write(('\t'.join(res)).encode('utf-8') + '\n')
