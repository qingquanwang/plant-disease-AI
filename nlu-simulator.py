#!/usr/bin/python
import argparse
import pprint
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
import os, sys

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='nlu simulator', usage='''
                ./nlu-simulator.py -d dicFile
                                   -r ruleFile
                                   -t greedy,ruleTagger
                                   -p zhBookPreprocessor"
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='./data/build/name.dic',
                        help='dictionary file path')
    parser.add_argument('--r', type=str,
                        default='./data/test/test.rule',
                        help='rule file path')
    parser.add_argument('--t', type=str,
                        default='greedy',
                        help='taggers')
    parser.add_argument('--p', type=str,
                        default=None,
                        help='zhBookPreprocessor')
    args = parser.parse_args()
    '''
    dic = DictManager()
    dic.load_dict(args.d)
    nlu = NLU(dic)
    for line in sys.stdin.readlines():
        rawText = line.strip().decode('utf-8')
        anaList = nlu.analysis(rawText)

        res = []
        for ana in anaList:
            res.append(ana.dumpBestSeq())
        print rawText.encode('utf-8') + '\t' + ('|'.join(res)).encode('utf-8')
    '''
