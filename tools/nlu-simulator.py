#!/usr/bin/python
import argparse
import pprint
import os,sys
from os.path import realpath, join, dirname
sys.path.insert(0, join(dirname(realpath(__file__)), '../'))
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.semantic import *

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='nlu simulator', usage='''
                ./nlu-simulator.py --d dicFile
                                   --r ruleFile
                                   --t greedy,ruleTagger
                                   --w removeTok
                                   --p [zhBook|govTitle]
                                   --s semanticsFile
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='./data/test/name.dic',
                        help='dictionary file path')
    parser.add_argument('--r', type=str,
                        default='./data/test/RuleEngine/rule0',
                        help='rule file path')
    parser.add_argument('--t', type=str,
                        default='greedy,ruleTagger',
                        help='taggers')
    parser.add_argument('--w', type=str,
                        default='',
                        help='rewriters')
    parser.add_argument('--p', type=str,
                        default='zhBook',
                        help='zhBook')
    parser.add_argument('--s', type=str,
                        default='./data/test/Semantics/wx-test-semantics.json',
                        help='semantics file')
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
    
    if args.w != '':
        for rewriterName in args.w.split(','):
            if rewriterName == 'removeTok':
                rewriter = RemoveTokRewriter()
                nlu.appendRewriter(rewriter)
            else:
                raise NameError('unknown rewriter: ' + rewriterName)
    semantic = SemanticBase()
    semantic.loadSemanticRules(args.s)

    for line in sys.stdin.readlines():
        rawText = line.strip().decode('utf-8')
        anaList = []
        nlu.tagText(anaList, rawText, True)
        res = []
        blocks = {}
        semantic.extract(anaList, blocks, '')
        blockStr = json.dumps(blocks, encoding='utf-8')
        for ana in anaList:
            #pp.pprint(ana)
            #if ana is None:
            #    continue
            analysis = ana.dumpBestSeq(True)
            #analysis = ana.dumpAllSeq()
            #print analysis.encode('utf-8')
            res.append(analysis)
        print rawText.encode('utf-8') + '\t' + blockStr + '\t' + ('\001'.join(res)).encode('utf-8')
        #pp.pprint(blocks)

