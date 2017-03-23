#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import sys
import fire
import simplejson as json
import jsonpickle


class Fact(object):

    def __init__(self, key, value):
        self.key = key
        list_value = []
        if not isinstance(value, list):
            list_value.append(value)
        else:
            list_value = value
        self.value = list_value

    @classmethod
    def from_json(cls, jsonobj):
        key = jsonobj.keys()[0]
        fact = Fact(key, jsonobj[key])
        return fact

    def __str__(self):
        value_str = u'[' + u','.join(self.value) + u']'
        return '{%s: %s}' % (self.key.encode('utf-8'), value_str.encode('utf-8'))


class FactJSONDecoder(json.JSONDecoder):

    def decode(self, json_string):
        default_obj = super(EvidenceJSONDecoder, self).decode(json_string)
        fact = Fact.from_json(default_obj)
        return fact


class Evidence(object):

    Pending = 0
    Satisfied = 1
    Conflicted = -1

    def __init__(self, facts):
        self.facts = list(facts)
        self.dict = {}
        for fact in self.facts:
            self.dict[fact.key] = fact.value

    @classmethod
    def from_json(cls, jsonobj):
        facts = []
        for factobj in jsonobj:
            fact = Fact.from_json(factobj)
            facts.append(fact)
        evidence = cls(facts)
        return evidence

    def relation(self, answers):
        has_conflict = False
        # print('process evidence: {}'.format(self))
        for answer in answers:
            # print('process answer:{}'.format(answer))
            # 该evidenc的keys()是某条回答的keys()的子集
            if set(self.dict.keys()).issubset(answer.dict.keys()):
                satisfied = True
                # 答案中有交集
                for key in self.dict:
                    inter = set(self.dict[key]).intersection(set(answer.dict[key]))
                    if len(inter) == 0:
                        has_conflict = True
                        satisfied = False
                        # print('conflicted: evidence={}, answer={}'.format(self, answer))
                        break
                    else:
                        # print('satisfied: found intersection: {}'.format(inter))
                        pass
                if satisfied:
                    return Evidence.Satisfied
        # 优先判断时候有满足的evidence，没有的话处理conflict
        if has_conflict:
            return Evidence.Conflicted
        return Evidence.Pending

    def __str__(self):
        temp = ''
        for fact in self.facts:
            temp = temp + str(fact)
        return '[' + temp + ']'


class EvidenceJSONDecoder(json.JSONDecoder):

    def decode(self, json_string):
        default_obj = super(EvidenceJSONDecoder, self).decode(json_string)
        evidence = Evidence.from_json(default_obj)
        return evidence


class Hypothesis(object):

    def __init__(self, name, evidences):
        self.evidences = evidences
        self.name = name
        self.satisfied = []
        self.conflicted = []
        self.pending = []

    @classmethod
    def from_json(cls, jsonobj):
        name = jsonobj['hypo']
        evidences = []
        for evidenceobj in jsonobj['evidences']:
            evidence = Evidence.from_json(evidenceobj)
            evidences.append(evidence)
        hypo = cls(name, evidences)
        return hypo

    def process_answer(self, answers):
        for evidence in self.evidences:
            result = evidence.relation(answers)
            if result == Evidence.Conflicted:
                self.conflicted.append(evidence)
            elif result == Evidence.Satisfied:
                self.satisfied.append(evidence)
            else:
                self.pending.append(evidence)

    def status(self):
        print(u'hypo: {}, satified: {}, conflict: {}, pending: {}'.format(self.name, len(self.satisfied), len(self.conflicted), len(self.pending)))

    def __str__(self):
        temp = ''
        for evidence in self.evidences:
            temp = temp + ' ' + str(evidence) + '\n'
        return self.name.encode('utf-8') + ': \n' + temp


class HypothesisJSONDecoder(json.JSONDecoder):

    def decode(self, json_string):
        default_obj = super(HypothesisJSONDecoder, self).decode(json_string)
        evidence = Hypothesis.from_json(default_obj)
        return evidence


def make_deduction(answerpath, evidencepath):
    # 初始化answer
    print('answers: ')
    answers = []
    with open(answerpath, mode='r') as f:
        jsonobj = json.load(f)
        for answerobj in jsonobj:
            answer = Evidence.from_json(answerobj)
            print(answer)
            answers.append(answer)

    # 初始化evidence -> hypo字典
    print('hypos: ')
    hypos = []
    with open(evidencepath, mode='r') as f:
        jsonobj = json.load(f)
        for hypoobj in jsonobj['hypos']:
            hypo = Hypothesis.from_json(hypoobj)
            print(hypo)
            hypo.process_answer(answers)
            hypo.status()
            hypos.append(hypo)


def test_jsonpickle():
    # 不与采用，要使用类似{"py/object": "__main__.Fact", "value": "value", "key": "key"}而不是单纯的json
    fact = Fact('key', 'value')
    fact_json = jsonpickle.encode(fact)
    print(fact_json)
    fact_from_json = jsonpickle.decode(fact_json)
    print(fact_from_json)


def test_json():
    jsonstr = u'{"hypo": ["我是", "点点滴滴"]}'
    fact = json.loads(jsonstr, object_hook=Fact.from_json)
    print(fact)
    jsonstr = u'[{"location": ["果肉","果心"]},{"shape": ["水渍状"]},{"color": ["褐色"]}]'
    evidences = json.loads(jsonstr, cls=EvidenceJSONDecoder)
    print(evidences)
    jsonstr = u'{"hypo":"水心病","evidences":[[{"harmplants":["果心","果面","果肉"]}],[{"location":["果肉","果心"]},{"shape":["水渍状"]},{"color":["褐色"]}],[{"taste":["稍甜","酒精味"]}]]}'
    hypo = json.loads(jsonstr, cls=HypothesisJSONDecoder)
    print(hypo)


if __name__ == '__main__':
    fire.Fire()
    # test_jsonpickle()
    # test_json()
