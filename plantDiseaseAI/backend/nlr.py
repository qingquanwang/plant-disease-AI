# -*- coding: utf-8 -*-
import hanzi
import pprint

pp = pprint.PrettyPrinter(indent = 2)

# Question Template or Ack Template
class Template(object):
    def __init__(self):
        self._toks = []
        self._type = []
    def append_token(self, symbol, t='tok'):
        self._toks.append(symbol)
        self._type.append(t)
    def load_template_sent(self, sent):
        toks = list(sent)
        num = len(toks)
        i = 0
        while i < num:
            if toks[i] == '{':
                #found symbol
                j = i+1
                symbols = []
                while(toks[j] != '}'):
                    symbols.append(toks[j])
                    j = j+1
                self.append_token(''.join(symbols), 'symbol')
                i = j+1
            else:
                self.append_token(toks[i])
                i = i+1
    def generate_reply(self, env):
        res = []
        num = len(self._toks)
        for i in range(num):
            if self._type[i] == 'tok':
                res.append(self._toks[i])
            else:
                if self._toks[i] in env:
                    res.append(u'\u3001'.join(env[self._toks[i]]))
                else:
                    res.append('{' + self._toks[i] + '}')
        return ''.join(res)

class NLR(object):
    def __init__(self):
        self._templates = {}
    # templateId \t template: a b c {d} e?
    def load_template(self, file_path):
        with open(file_path, 'r') as fd:
            for line in fd.readlines():
                (template_id, template_sent) = line.strip('\n').decode('utf-8').split('\t')
                template = Template()
                template.load_template_sent(template_sent)
                self._templates[template_id] = template
    def use_template(self, templateId, env):
        if templateId in self._templates:
            return self._templates[templateId].generate_reply(env)
        else:
            return None
