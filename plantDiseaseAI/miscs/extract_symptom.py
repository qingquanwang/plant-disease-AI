#!/usr/bin/env python
# -*- coding: utf-8 -*-

import fire
import simplejson as json

delimiter = u'|'
separator = u'\t'
print_pattern = u'{}, {}, {}'


def pstr(msg):
    print(msg.encode('utf-8'))


def node_to_list(node, hypothesis, prefix=u''):
    if isinstance(node, int):
        node = unicode(node)
    if isinstance(node, unicode):
        node = node.replace(u',', u'COMMA')
        pstr(print_pattern.format(prefix, node, hypothesis))
        return
    elif isinstance(node, list):
        if len(node) == 0:
            return
        for item in node:
            node_to_list(item, hypothesis, prefix)
    elif isinstance(node, dict):
        if len(node) == 0:
            return
        for key in node:
            new_prefix = prefix + delimiter + key
            node_to_list(node[key], hypothesis, new_prefix)
    else:
        pstr(u'unexpected type: {}'.format(type(node)))


def extract_node(fpath, key_of_interest):
    '''
    从.json文件中抽取symptom
    '''
    with open(fpath) as f:
        json_obj = json.load(f)
    # print(json_obj)
    for key in json_obj.keys():
        node = json_obj[key]
        if key_of_interest in node.keys():
            node = json_obj[key][key_of_interest]
            node_to_list(node, key)
        else:
            pstr(u'{} key of interest not found'.format(key))
            exit()


if __name__ == '__main__':
    fire.Fire()
