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
                                   -s state-definition -i stateId -w "k1:v1,v2|k2:v3,v4"
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='./data/build/name.dic',
                        help='dictionary file path')
    parser.add_argument('--s', type=str,
                        default='./data/state-def.json',
                        help='state definition file path')
    parser.add_argument('--i', type=str,
                        default=None,
                        help='current stateId')
    parser.add_argument('--w', type=str,
                        default='',
                        help='whiteboard variables')
    args = parser.parse_args()
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
