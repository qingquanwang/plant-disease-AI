# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.LangCore import *
from plantDiseaseAI.backend.semantic.SemanticAnalysis import *
import pprint

pp = pprint.PrettyPrinter(indent = 2)

class SemanticBase(Semantic):
    def __init__(self):
        self._domainRules = {}
    def loadSemanticRules(self, fileName):
        with open(fileName, 'r') as fd:
            domainRules = json.load(fd, encoding='utf-8')
            for (domain, rules) in domainRules.items():
                if domain not in self._domainRules:
                    self._domainRules[domain] = []
                for r in rules:
                    sr = SemanticRule()
                    sr.initRule(r)
                    self._domainRules[domain].append(sr)

    def extract(self, anaList, semantics, domain=''):
        for ana in anaList:
            self.extract_analysis(ana, semantics, domain)

    def extract_analysis(self, analysis, semantics, domain=''):
        if domain == '':
            for d in self._domainRules:
                hitDomain = self.extract_analysis(analysis, semantics, d)
                if hitDomain:
                    return True

        elif domain in self._domainRules:
            rules = self._domainRules[domain]
            for rule in rules:
                (hit, res) = rule.execute(analysis)
                #print 'Debug: ' + rule._name + ':' + str(hit)
                if hit:
                    #pp.pprint(res)
                    semantics.update(res)
                    #pp.pprint(semantics)
                    return True
        else:
            raise NameError('domain name is unknown: ' + domain)
        return False
