#!/usr/bin/python
# -*- coding: utf-8 -*-
import argparse
import pprint
import os,sys
from os.path import abspath, join, dirname

sys.path.insert(0, join(abspath(dirname('__file__')), 'plantDiseaseAI/backend'))
sys.path.insert(0, join(abspath(dirname('__file__')), 'plantDiseaseAI/backend/handler'))

from plantDiseaseAI.backend.DictManager import *
from plantDiseaseAI.backend.nlu import *
from plantDiseaseAI.backend.nlr import *
from plantDiseaseAI.backend.Dialog import *
from plantDiseaseAI.backend.Interaction import *

pp = pprint.PrettyPrinter(indent = 2)

def doActions(actions):
    for act in actions:
        act.debugMsg()
        if act._type == 'ShowPlainText':
            print act._text.encode('utf-8')
        else:
            continue

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description='dialog simulator', usage='''
                ./dialog-simulator.py -d dicFile -t template_file
                        -s state-definition -i currentTask -w "k1:v1,v2|k2"v3,v4"
                问天气: python dialog-simulator.py --s data/state-def-wx.json --d data/test/name.dic
                ''', formatter_class = argparse.RawTextHelpFormatter)
    parser.add_argument('--d', type=str,
                        default='./data/build/name.dic',
                        help='dictionary file path')
    parser.add_argument('--t', type=str,
                        default='./data/reply-template',
                        help='reply template file path')
    parser.add_argument('--s', type=str,
                        default='./data/state-def.json',
                        help='state definition file path')
    parser.add_argument('--i', type=str,
                        default='Welcome',
                        help='current taskId')
    parser.add_argument('--w', type=str,
                        default='',
                        help='whiteboard variables')

    args = parser.parse_args()
    dic = DictManager()
    dic.load_dict(args.d)
    nlu = NLU(dic)
    nlu.appendTagger(GreedyTagger())
    tagger = RuleTagger()
    ruleFile = './data/test/RuleEngine/rule0'
    tagger.loadRules(ruleFile)
    nlu.appendTagger(tagger)

    nlr = NLR()
    nlr.load_template(args.t)
    dialog = DialogManager()
    dialog.addModule("NLU", nlu)
    dialog.addModule("NLR", nlr)
    dialog.loadHandler(args.s)

    session = WhiteBoard()
    session.deserialize(args.w.decode('utf-8'))
    state = State()
    state.setStartState(args.i)
    state._session = session


    userInput = None
    actions = []
    state.debugMsg()

    dialog.execute(state, userInput, actions)
    doActions(actions)

    # Interaction
    while True:
        line = raw_input('usr > ')
        text = line.strip('\n').decode('utf-8')
        userInput = UserInput('Text', text)
        actions = []
        dialog.execute(state, userInput, actions)
        state.debugMsg()
        doActions(actions)
        if state._status == 'END':
            print "Bye-Bye"
            break
