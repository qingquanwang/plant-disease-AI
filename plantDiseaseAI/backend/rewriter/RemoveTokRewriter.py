# -*- coding: utf-8 -*-
import pprint
from plantDiseaseAI.backend.LangCore import Span
from plantDiseaseAI.backend.LangCore import Rewriter
from plantDiseaseAI.backend.Tagging import SpanGraph

pp = pprint.PrettyPrinter(indent=2)

class RemoveTokRewriter(Rewriter):
    def __init__(self):
        pass

    def walk(self, spanGraph, rewriteGraph, pos, rpos, nonTrivialPos):
        if pos in spanGraph._startMap:
            spanNum = len(spanGraph._startMap[pos])
            if pos not in nonTrivialPos:
                self.walk(spanGraph, rewriteGraph, pos+1, rpos, nonTrivialPos)
            else:
                for spanId in spanGraph._startMap[pos]:
                    span = spanGraph._spans[spanId]
                    # copy span, change _start
                    newspan = Span(rpos, span._len, span._type, span._text)
                    # add new span into rewriteGraph
                    rewriteGraph._spans.append(newspan)
                    spanId = len(rewriteGraph._spans) - 1
                    if rpos in rewriteGraph._startMap:
                        rewriteGraph._startMap[rpos].append(spanId)
                    else:
                        rewriteGraph._startMap[rpos] = []
                        rewriteGraph._startMap[rpos].append(spanId)
                    self.walk(spanGraph, rewriteGraph, pos+span._len, rpos+newspan._len, nonTrivialPos)
        else:
            return

    def rewrite(self, spanGraph):
        # 1. calculate position covered by non-trivial span
        keepTok = {}
        for i in range(len(spanGraph._spans)):
            span = spanGraph._spans[i]
            start_pos = span._start
            if span._type != 'tok':
                for l in range(span._len):
                    pos = start_pos + l
                    if pos in spanGraph._startMap:
                        keepTok[pos] = True
        #pp.pprint(keepTok)
        # 2. calculate new position offset, idx(old_position) -> new_position
        offset = []
        pos = 0
        newpos = 0
        while pos in spanGraph._startMap:
            offset.append(newpos)
            if pos in keepTok:
                newpos = newpos + 1
            pos = pos + 1

        graph = SpanGraph()
        collapseOffset = 0
        for span in spanGraph._spans:
            start_pos = span._start
            if start_pos in keepTok:
                pos = offset[start_pos]
                newspan = Span(pos, span._len, span._type, span._text)
                graph._spans.append(newspan)
                spanId = len(graph._spans) - 1
                if pos not in graph._startMap:
                    graph._startMap[pos] = []
                graph._startMap[pos].append(spanId)
        return graph
