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
                        default='./data/test/name.dic',
                        help='dictionary file path')
    parser.add_argument('--r', type=str,
                        default='./data/test/RuleEngine/rule0',
                        help='rule file path')
    parser.add_argument('--t', type=str,
                        default='greedy',
                        help='taggers')
    parser.add_argument('--p', type=str,
                        default='zhBook',
                        help='zhBook')
    args = parser.parse_args()

    
    dic = DictManager()
    dic.load_dict(args.d)

    nlu = NLU(dic)
    nlu.setPreprocessor(args.p)
    for taggerName in args.t.split(','):
        if taggerName == 'greedy':
            tagger = GreedyTagger()
            nlu.appendTagger(tagger)
        elif taggerName == 'ruleTagger':
            tagger = RuleTagger()
            ruleFile = args.r
            tagger.loadRules(ruleFile)
            nlu.appendTagger(tagger)
        else:
            raise NameError('unknown tagger: ' + taggerName)

    for line in sys.stdin.readlines():
        rawText = line.strip().decode('utf-8')
        anaList = []
        nlu.tagText(anaList, rawText, True)
        res = []
        for ana in anaList:
            #pp.pprint(ana)
            #if ana is None:
            #    continue
            analysis = ana.dumpBestSeq(True)
            #print analysis.encode('utf-8')
            res.append(analysis)
        print rawText.encode('utf-8') + '\t' + ('\001'.join(res)).encode('utf-8')

