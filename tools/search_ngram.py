#!/usr/bin/python

import re
import copy
import os,sys
import pprint

pp = pprint.PrettyPrinter(indent=4)

def ngram_search(text, keyword, n=2, begin=False):
    ngrams = []
    toks = list(text)
    tok_num = len(toks)
    for i in range(tok_num - n + 1):
        ngram = ''.join(toks[i:i+n])
        ngrams.append(ngram)
    res = []
    for ngram in ngrams:
        #print ngram.encode('utf-8')
        if (begin == True) and ngram.startswith(keyword):
            res.append(ngram)
        elif (begin == False) and ngram.endswith(keyword):
            res.append(ngram)
        else:
            continue
    #pp.pprint(res)
    return res
def main():
    ngram_freq = {}
    keyword = ''
    num = 2
    begin = False
    if len(sys.argv) >= 2:
        keyword = sys.argv[1].decode('utf-8')
    if len(sys.argv) >= 3:
        num = int(sys.argv[2])
    if len(sys.argv) >= 4:
        if sys.argv[3] == 'true':
            begin = True
    for line in sys.stdin.readlines():
        line = line.strip().decode('utf-8')
        if line != '':
            norm_line = ''.join(line.split(' '))
            res = ngram_search(norm_line, keyword, num, begin)
            if len(res) > 0:
                for r in res:
                    if r in ngram_freq:
                        ngram_freq[r] = ngram_freq[r] + 1
                    else:
                        ngram_freq[r] = 1
    for ngram in ngram_freq:
        print ngram.encode('utf-8') + '\t' + str(ngram_freq[ngram])

if __name__ == '__main__':
    main()
