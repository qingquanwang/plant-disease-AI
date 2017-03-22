# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.Tagging import *
import pprint

pp = pprint.PrettyPrinter(indent = 2)

# TODO
def semantic_mainTask(anaList, env):
    plantName = ''
    diseaseName = ''
    intent = ''
    for ana in anaList:
        spans, annotation = ana.getBestSeq(0.5)
        if spans is None:
            continue
        for span in spans:
            if span._type == '/plant':
                plantName = span._text
            elif span._type == '/disease':
                diseaseName = span._text
            elif span._type == '/intent':
                intent = span._text
            else:
                continue

        if plantName == '' and diseaseName == '' and intent == '':
            return False

        if diseaseName != '':
            env.override('diseaseName',  diseaseName)
        if plantName != '':
            env.override('plantName', plantName)
        if intent != '':
            env.append('intent', intent)
        if intent == 'Diagnostic':
            env.override('taskType',  'Diagnostic')
        else:
            env.override('taskType', 'Info')
        return True
#semantic_
