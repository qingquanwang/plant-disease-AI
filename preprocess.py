#!/usr/bin/python
import argparse
import pprint
from plantDiseaseAI.backend.preprocessor import *
import os, sys

pp = pprint.PrettyPrinter(indent = 2)

def dumpToks(toks, split):
    res = []
    for tok in toks:
        if tok._type == 'splitter':
            if split == True:
                print '\002'.join(res).encode('utf-8')
                res[:] = []
            else:
                res.append(tok._text + '\001' + tok._type)
        else:
            res.append(tok._text + '\001' + tok._type)
    if len(res) > 0:
        print '\002'.join(res).encode('utf-8')

def createPreprocessor(name):
    if name == 'zhBook':
        return ZhBookPreprocessor()
    else:
        raise NameError('Unknown name of preprocessor:[' + name + ']')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='preprocess text', usage='''
                ./preprocess.py --i input
                                --p preprocessor
                                --s"
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--i', type=str,
                        default='-',
                        help='input file or - (stdin)')
    parser.add_argument('--p', type=str,
                        default='zhBook',
                        help='[zhBook]')
    parser.add_argument('--s', dest = 's', action = 'store_true')

    args = parser.parse_args()

    preprocessor = createPreprocessor(args.p)
    
    inputFile = args.i
    split = args.s

    if inputFile == '-':
        for line in sys.stdin.readlines():
            toks = []
            preprocessor.preprocess(line.strip('\n').decode('utf-8'), toks)
            dumpToks(toks, split)
    else:
        with open(inputFile, 'r') as fd:
            for line in fd.readlines():
                rawText = line.decode('utf-8').strip('\n')
                toks = []
                preprocessor.preprocess(rawText, toks)
                dumpToks(toks, split)
