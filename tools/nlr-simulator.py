#!/usr/bin/python
import argparse
import pprint
import os,sys
from os.path import realpath, join, dirname
sys.path.insert(0, join(dirname(realpath(__file__)), '../'))
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Interaction import *

pp = pprint.PrettyPrinter(indent = 2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='nlr simulator', usage='''
                ./nlr-simulator.py -t template_file -w "k1:v1,v2|k2:v3,v4" templateId
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--t', type=str,
                        default='./data/test/reply-template',
                        help='reply template file path')
    parser.add_argument('templateId', type=str, nargs='?',
                        help='template id')
    parser.add_argument('--w', type=str,
                        default='',
                        help='whiteboard variables')
    args = parser.parse_args()
    nlr = NLR()
    nlr.load_template(args.t)
    session = WhiteBoard()
    session.deserialize(args.w.decode('utf-8'))
    print (nlr.use_template(args.templateId, session._env)).encode('utf-8')
