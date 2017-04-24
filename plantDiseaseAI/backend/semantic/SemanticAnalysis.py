# -*- coding: utf-8 -*-
from plantDiseaseAI.backend.LangCore import *
from plantDiseaseAI.backend.Tagging import *
import json
import pprint

pp = pprint.PrettyPrinter(indent = 2)

class SemanticCondition(object):
    def __init__(self):
        pass
    def evalCondition(self, seq, inputGraph):
        pass

class SemanticAnnotationCondition(SemanticCondition):
    def __init__(self):
        pass
    # op is actually we only support =
    def setAnnotationCondition(self, key, op = None, value = None):
        self._key = key
        self._op = op
        self._value = value
    def evalCondition(self, seq, inputGraph):
        dic = seq._annotation
        kLevel = self._key.split('.')
        curObj = dic
        for i in range(len(kLevel)):
            k = kLevel[i]
            if k in curObj:
                tmp = curObj[k]
                curObj = tmp
                if i == (len(kLevel) - 1):
                    if self._op is None:
                        return True
                    else:
                        return curObj == self._value
            else:
                return False

class SemanticSpanSeqCondition(SemanticCondition):
    def __init__(self):
        pass
        self._spans = []
        self._order = 'permuted'
    # spanSeq: span1:<type^text(optional)>|span2|span3
    def setSpanSeqCondition(self, spanSeq, order='permuted'):
        spans = spanSeq.split('|')
        for s in spans:
            s = s.strip('<')
            s = s.strip('>')
            if ':' in s:
                spanType, spanText = s.split('^')
                spanText = spanText.strip('"')
                self._spans.append(Span(0, 0, spanType, spanText))
            else:
                self._spans.append(Span(0, 0, s, ''))
        if order not in ['permuted', 'ordered']:
            raise TypeError('unknown seq order type: ' + order)
        self._order = order
    def evalCondition(self, seq, inputGraph):
        spanNum = len(self._spans)
        match = []
        for i in range(spanNum):
            match.append(False)
        curpos = 0
        matchedNum = 0
        for spanId in seq._spans:
            text = inputGraph._spans[spanId]._text
            spanType = inputGraph._spans[spanId]._type
            if self._order == 'ordered':
                if spanType == self._spans[i]._type:
                    if self._spans[i]._text != '':
                        if text == self._spans[i]._text:
                            #matched
                            matchedNum = matchedNum + 1
                            match[curpos] = True
                            curpos = curpos + 1
                            if matchedNum == spanNum:
                                return True
                        else:
                            # not matched
                            continue
                    else:
                        #matched
                        matchedNum = matchedNum + 1
                        match[curpos] = True
                        curpos = curpos + 1
                        if matchedNum == spanNum:
                            return True
                else:
                    continue
            else:
                for i in range(spanNum):
                    if match[i] == True:
                        #we already match this span check
                        continue
                    elif spanType == self._spans[i]._type:
                        if self._spans[i]._text != '':
                            if text == self._spans[i]._text:
                                #matched
                                matchedNum = matchedNum + 1
                                match[i] = True
                                if matchedNum == spanNum:
                                    return True
                            else:
                                # not matched
                                continue
                        else:
                            #matched
                            matchedNum = matchedNum + 1
                            match[i] = True
                            if matchedNum == spanNum:
                                return True
                    else:
                        continue
        return False

class SemanticExtracter(object):
    def __init__(self):
        pass
    def extract(self, dic, seq, inputGraph):
        return False

class SemanticAnnExtracter(SemanticExtracter):
    def __init__(self):
        self._extractions = []
        
    def appendExtraction(self, key, valueName, option = 'required', store = 'override', plainText=False):
        self._extractions.append((key, valueName, option, store, plainText))

    # Note: this will merge slots with the same name, sometimes this is not what we expected
    def getAssignValue(self, seq, key, plainText):
        assignValue = None
        curObj = seq._annotation
        if plainText:
            assignValue = plainText
            return assignValue
        kLevel = key.split('.')
        levelNum = len(kLevel)
        for i in range(levelNum):
            k = kLevel[i]
            if k in curObj:
                if i == levelNum - 1:
                    assignValue = curObj[k]
                    break
                else:
                    curObj = curObj[k]
            else:
                break
        if isinstance(assignValue, list):
            assignValue = ''.join(assignValue)
        return assignValue

    def assignValue(self, dic, valueName, assignValue, store):
        vLevel = valueName.split('.')
        levelNum = len(vLevel)
        curObj = dic
        for i in range(levelNum):
            k = vLevel[i]
            if k in curObj:
                if i == (levelNum - 1):
                    if store == 'override':
                        curObj[k] = assignValue
                    else:
                        curObj[k].append(assignValue)
                    return
            else:
                if i == (levelNum - 1):
                    if store == 'override':
                        curObj[k] = assignValue
                    else:
                        curObj[k] = [assignValue]
                    return
                else:
                    curObj[k] = {}
            curObj = curObj[k]

    def extract(self, dic, seq, inputGraph):
        for extraction in self._extractions:
            (key, valueName, option, store, plainText) = extraction
            assignValue = self.getAssignValue(seq, key, plainText)
            #print 'Debug[extraction]: key:[' + key + ']  valueName:['+valueName + ']'
            #pp.pprint(assignValue)
            if (assignValue is None) and (option == 'required'):
                return False
            elif assignValue is None:
                continue
            else:
                self.assignValue(dic, valueName, assignValue, store)
        return True

class SemanticSeqExtracter(SemanticExtracter):
    def __init__(self):
        self._extractions = []
    #special key of span is 'text', we assign the plain text
    def appendExtraction(self, spanAttr, valueName, option = 'required', store = 'override'):
        #print 'appendExtraction: ' + spanAttr
        if spanAttr.startswith('<'):
            (span, key) = spanAttr.split('.')
            span = span.strip('<')
            span = span.strip('>')
            self._extractions.append((span, key, valueName, option, store))
        else:
            self._extractions.append((None, spanAttr, valueName, option, store))

    def getAssignValue(self, seq, inputGraph, spanType, key):
        if spanType is None:
            return key

        assignValue = None
        for spanId in seq._spans:
            if spanType == inputGraph._spans[spanId]._type:
                if key == 'text':
                    assignValue = inputGraph._spans[spanId]._text
                else:
                    if key in inputGraph._spans[spanId]._attrs:
                        assignValue = inputGraph._spans[spanId]._attrs[key]
            else:
                continue
        return assignValue

    def assignValue(self, dic, valueName, assignValue, store):
        curObj = dic
        vLevel = valueName.split('.')
        levelNum = len(vLevel)
        for i in range(levelNum):
            k = vLevel[i]
            if k in curObj:
                if i == (levelNum - 1):
                    if store == 'override':
                        curObj[k] = assignValue
                    else:
                        curObj[k].append(assignValue)
            else:
                if i == (levelNum - 1):
                    if store == 'override':
                        curObj[k] = assignValue
                    else:
                        curObj[k] = [assignValue]
                    break
                else:
                    curObj[k] = {}
            #pp.pprint(curObj)
            curObj = curObj[k]
    def extract(self, dic, seq, inputGraph):
        for extraction in self._extractions:
            (spanType, key, valueName, option, store) = extraction
            #print 'extracting :' + str(spanType) + ' ' + str(key) + ' ' + str(valueName)
            assignValue = self.getAssignValue(seq, inputGraph, spanType, key)
            if (assignValue is None) and (option == 'required'):
                #print 'required variable is none'
                return False
            elif assignValue is None:
                continue
            else:
                self.assignValue(dic, valueName, assignValue, store)
        return True

class SemanticRule(object):
    def __init__(self, topK=1, threshold=0.0, sources = ''):
        self._topK = topK
        self._threshold = threshold
        self._sources = []
        if sources == '':
            pass
        else:
            for s in sources.split('|'):
                self._sources.append(s)
        self._conditions = []
        self._extractions = []
    
    def addCondition(self, condition):
        self._conditions.append(condition)

    def addExtraction(self, extracter):
        self._extractions.append(extracter)

    def setSources(self, sources):
        if sources == '':
            pass
        else:
            for s in sources.split('|'):
                self._sources.append(s)

    def initRule(self, obj):
        self._name = obj['Name']
        self._topK = int(obj['topK'])
        self._threshold = float(obj['threshold'])
        if 'sources' in obj:
            self.setSources(obj['sources'])

        conditionType = obj['conditionType']
        for condition in obj['conditions']:
            if conditionType == 'annotation':
                c = SemanticAnnotationCondition()
                op = '=='
                (k, v) = condition.split(op)
                k = k.strip('$')
                k = k.strip('{')
                k = k.strip('}')
                c.setAnnotationCondition(k, op, v)
                self.addCondition(c)
            elif conditionType == 'sequence':
                c = SemanticSpanSeqCondition()
                (spanSeq, order) = condition.split(':')
                c.setSpanSeqCondition(spanSeq, order)
                self.addCondition(c)
            else:
                raise TypeError('unknown condition type: ' + conditionType)

        extractionType = obj['extractionType']
        for extraction in obj['extractions']:
            if extractionType == 'annotation':
                e = SemanticAnnExtracter()
                (expr, option, store) = extraction.split(':')
                (valueName, key) = expr.split('=')
                plainText = False
                if key.startswith('$'):
                    plainText = False
                    key = key.strip('$')
                    key = key.strip('{')
                    key = key.strip('}')
                else:
                    plainText = True
                e.appendExtraction(key, valueName, option, store, plainText)
                self.addExtraction(e)
            elif extractionType == 'sequence':
                e = SemanticSeqExtracter()
                (expr, option, store) = extraction.split(':')
                (valueName, spanAttr) = expr.split('=')
                e.appendExtraction(spanAttr, valueName, option, store)
                self.addExtraction(e)
            else:
                raise TypeError('unknown extraction type: ' + extractionType)

    def execute(self, analysis):
        seqNum = len(analysis._seqs)
        inputGraph = analysis._graph
        for i in range(seqNum):
            dic = {}
            if i >= self._topK:
                return (False, {})
            seq = analysis._seqs[i]
            score = seq._prob
            if score < self._threshold:
                return (False, {})
            if len(self._sources) > 0 and seq._source not in self._sources:
                continue
            hit = True
            for c in self._conditions:
                if c.evalCondition(seq, inputGraph) == False:
                    hit = False
                    break
            if not hit:
                continue
            status = True
            for e in self._extractions:
                status = e.extract(dic, seq, inputGraph)
                #print '[Debug] Status:' + str(status)
                if not status:
                    break
                else:
                    #pp.pprint(dic)
                    continue
            if status:
                return (True, dic)

        return (False, {})
