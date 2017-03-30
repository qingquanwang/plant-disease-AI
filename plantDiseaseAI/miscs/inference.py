#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import fire


delimiter = u','
index_symptom = 0
index_value = 1
index_hypothsis = 2


def draw_inference(dictpath, evidencepath):
    # 初始化已经确定的evidence
    evidences_dic = {}
    with open(evidencepath) as f:
        for line in f:
            line = line.decode('utf-8').strip()
            print(line)
            # evidences.append(line)
            evidences_dic[line.split(delimiter)[index_symptom]] = line.split(delimiter)[index_value]
    # print(evidences_dic)
    # 初始化所有evidence -> hypothesis表
    dict_strs = []
    qualified_hs = set()
    useless_keys = set()
    with open(dictpath) as f:
        for line in f:
            line = line.decode('utf-8').strip()
            dict_strs.append(line)
            qualified_hs.add(line.split(delimiter)[index_hypothsis])
    # 根据已经确定的evidence处理evidence -> hypothesis表
    for key in evidences_dic:
        # value不为空时，不含有k,v的h项都要删除
        if evidences_dic[key]:
            temp = list(s.split(delimiter)[index_hypothsis] for s in dict_strs if key in s and evidences_dic[key] in s)
            temp = set(temp)
            qualified_hs = qualified_hs & temp
        # value为空时，k,v不再有参考价值
        else:
            useless_keys.add(key)
    print(u'qualified_hs(total={}): {}'.format(len(qualified_hs), u','.join(qualified_hs)))
    print(u'useless_keys: {}'.format(u','.join(useless_keys)))
    dict_strs = list(s for s in dict_strs if s.split(delimiter)[index_hypothsis] in qualified_hs and s.split(delimiter)[index_symptom] not in useless_keys)
    print(u'after processing, len(dict_strs) = {}'.format(len(dict_strs)))
    # 含有的k的h的个数最接近qualified_hs个数一半的key
    keys = set(list(s.split(delimiter)[index_symptom] for s in dict_strs))
    khs = {}
    closest_value = sys.maxint
    for key in keys:
        hypothesis = []
        for kvh in dict_strs:
            if key == kvh.split(delimiter)[index_symptom]:
                hypothesis.append(kvh.split(delimiter)[index_hypothsis])
        count = len(set(hypothesis))
        khs[key] = count
        if abs(count - len(qualified_hs) / 2.0) < abs(closest_value - len(qualified_hs) / 2.0):
            closest_value = count
    print(khs)
    print(u'closest_value = {}'.format(closest_value))
    # 在同时影响h最多的key中选取unique v最多的key
    # unique_v_count = 0
    for key in khs:
        if khs[key] == closest_value:
            # 计算unique v
            pass
            # values = set(list(s.split(delimiter)[index_value] for s in dict_strs if key == s.split(delimiter)[index_symptom))


if __name__ == '__main__':
    fire.Fire()
