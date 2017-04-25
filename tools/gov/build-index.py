#!/usr/bin/python
import argparse
import pprint
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
                                 --o outputFile
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='../../data/test/name.dic',
                        help='dictionary file path')
    parser.add_argument('--o', type=str,
                        default='./gov-index',
                        help='index file')

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

    for line in sys.stdin.readlines():
        fs = line.strip().decode('utf-8').split('\t')
        docId = fs[0]
        rawText = fs[2]
        anaList = []
        nlu.tagText(anaList, rawText, True)
        res = []
        blocks = {}
        semantic.extract(anaList, blocks, '')
        #pp.pprint(blocks)
        idxs = []
        attrs = []
        indexer.extractFeature(blocks, idxs, attrs)
        for idx in idxs:
            if idx in indexes:
                indexes[idx].append(docId)
            else:
                indexes[idx] = []
                indexes[idx].append(docId)
        docs[docId] = attrs
        '''
        blockStr = json.dumps(blocks, encoding='utf-8')
        for ana in anaList:
            analysis = ana.dumpBestSeq(True)
                        res.append(analysis)
        print rawText.encode('utf-8') + '\t' + blockStr + '\t' + ('\001'.join(res)).encode('utf-8')
        '''
    for idx in indexes:
        print 'idx:' + idx.encode('utf-8') + '\t' + ('\001'.join(indexes[idx])).encode('utf-8')
    for docId in docs:
        print 'doc:' + docId.encode('utf-8') + '\t' + ('\001'.join(docs[docId])).encode('utf-8')
