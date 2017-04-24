#!/usr/bin/python
import json
import os,sys
import pprint

pp = pprint.PrettyPrinter(indent = 2)

def build_reason_plan(obj, plans):
    domain = ''
    service = ''
    subject = ''
    city = ''
    condition = ''
    question = ''
    item = ''
    regulation = ''
    role = ''
    if 'domain' in obj:
        domain = obj['domain']
    if 'gov' in obj:
        obj = obj['gov']
    else:
        return (None, None)

    categories = []
    attrs = []
    if 'subject'in obj:
        subject = obj['subject']
        categories.append('subject=' + subject)
    if 'role' in obj:
        role = obj['role']
        categories.append('role=' + role)
    if 'service' in obj:
        service = obj['service']
        categories.append('service=' + service)
    if 'condition' in obj:
        condition = obj['condition']
        categories.append('condition=' + condition)
    if 'question' in obj:
        question = obj['question']
        attrs.append('question=' + question)
    if 'item' in obj:
        item = obj['item']
        attrs.append('item=' + item)
    if 'regulation' in obj:
        regulation = obj['regulation']
        attrs.append('regulation=' + regulation)
    return ('|'.join(categories) , '|'.join(attrs))
if __name__ == '__main__':
    stat = {}
    for line in sys.stdin.readlines():
        line = line.strip('\n').decode('utf-8')
        (title, blocks, seq) = line.split('\t')
        obj = json.loads(blocks, encoding='utf-8')
        plans = []
        (category, attr) = build_reason_plan(obj, plans)
        
        if category is None:
            sys.stderr.write('cannot handle: ' + title.encode('utf-8') + '\n')
        else:
            if category in stat:
                stat[category].append((title, attr))
            else:
                stat[category] = []
                stat[category].append((title, attr))

            #print (title + '\t' + category + '\t' + attr).encode('utf-8')
    for category in stat:
        num = len(stat[category])
        print category.encode('utf-8') + '\t' + 'number:' + str(num)
        for (title,attr) in stat[category]:
            print ('    ' + attr + '\t' + title).encode('utf-8')

