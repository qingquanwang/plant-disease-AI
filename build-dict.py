#!/usr/bin/python
import argparse
import pprint
from plantDiseaseAI.backend.DictManager import *

pp = pprint.PrettyPrinter(indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
               description='build dict', usage='''
               ./build-dict.py --data_root=./data/test/dict --output=./data/test/name.dic
               ''', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--data_root', type=str, 
                         default='./data/test/dict',
                         help='directory root of dict')
    parser.add_argument('--output', type=str,
                         default='./data/test/name.dic',
                         help='output path of dict')
    args = parser.parse_args()
    dic = DictManager()
    dic.compile_dict(args.data_root, args.output)
    #dicTest = DictManager()
    #dicTest.load_dict(args.output)
    #pp.pprint(dicTest._names)
