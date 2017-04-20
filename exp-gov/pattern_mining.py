#!/usr/bin/python
import os,sys
import pprint

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__':
    stat = {}
    for line in sys.stdin.readlines():
        spans = line.decode('utf-8').strip('\n').split('][')
        #pp.pprint(spans)
        res = []
        for spanText in spans:
            spanText = spanText.strip('[')
            spanText = spanText.strip(']')
            #print spanText.encode('utf-8')
            if spanText == '':
                continue
            (text, span_type) = spanText.split('|')
            res.append('<' + span_type + '>')
        sig = ''.join(res)
        if sig in stat:
            stat[sig] = stat[sig] + 1
        else:
            stat[sig] = 1
    for (k,v) in stat.items():
        print k + '\t' + str(v)
