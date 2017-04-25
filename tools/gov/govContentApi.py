#!/usr/bin/python

import argparse
import pprint
import math
from sets import Set
import os,sys
from os.path import realpath, join, dirname
sys.path.insert(0, join(dirname(realpath(__file__)), '../..'))
from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.semantic import *
from govTitleExtracter import *

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='build-index.py', usage='''
                ./build-index.py --d dicFile
                                 --i indexFile
                                 --c contentFile
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='../../data/test/name.dic',
                        help='dictionary file path')
    parser.add_argument('--i', type=str,
                        default='./gov-index',
                        help='index file')
    parser.add_argument('--c', type=str,
                        default='./gov_q',
                        help='content file')

    args = parser.parse_args()
    dic = DictManager()
    dic.load_dict(args.d)

    nlu = NLU(dic)
    nlu.setPreprocessor('govTitle')
    nlu.appendTagger(GreedyTagger())
    tagger = RuleTagger()
    tagger.loadRules('./gov-rule')
    nlu.appendTagger(tagger)
    
    nlu.appendRewriter(RemoveTokRewriter())

    semantic = SemanticBase()
    semantic.loadSemanticRules('./gov-semantics.json')

    indexes = {}
    docs = {}
    indexer = GovTitleExtracter()
    indexer.getIndexId(dic)
    indexer.loadIndex(args.i)
    indexer.loadContent(args.c)
    #pp.pprint(indexer._indexes)


    for line in sys.stdin.readlines():
        rawText = line.strip().decode('utf-8')
        anaList = []
        nlu.tagText(anaList, rawText, True)
        res = []
        blocks = {}
        semantic.extract(anaList, blocks, '')
        idxs = []
        attrs = []
        indexer.extractFeature(blocks, idxs, attrs)
        #pp.pprint(idxs)
        cands = []
        indexer.getCandidate(cands, idxs, attrs)
        print rawText.encode('utf-8')
        for cand in cands:
            doc = indexer._content[cand]
            print '  ' + cand.encode('utf-8') + '\t' + doc['title'].encode('utf-8')
