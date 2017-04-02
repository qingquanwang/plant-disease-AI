# -*- coding: utf-8 -*-
import pprint
from plantDiseaseAI.backend.LangCore import Preprocessor
from plantDiseaseAI.backend.LangCore import Token
import plantDiseaseAI.backend.lex as lex

pp = pprint.PrettyPrinter(indent=2)


class ZhBookPreprocessor(Preprocessor):

    tokens = (
        'DIGIT',
        'ZhWord',
        'EnWord',
        'SplitPunct',  # 断句
        'UnsplitPunct',  # 、
        'WordsQuot',   # 引号
        'BookQuo',  # 书名号
        'Reference'  #
    )

    # Tokens

    def t_DIGIT(self, t):
        ur'[-+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)'
        try:
            if ('.' in t.value):
                t.value = float(t.value)
            else:
                t.value = int(t.value)
        except ValueError:
            print("Digit value too large %s" % t.value)
            t.value = 0
        # print "parsed digit %s" % repr(t.value)
        return t

    def t_ZhWord(self, t):
        ur'[\u3007\u4e00-\u9fff]+'
        # print(u'parsed ZH word %s' % t.value)
        return t

    def t_EnWord(self, t):
        ur'[a-zA-Z]+([-_][a-zA-Z]*)*'
        # print(u'parsed En word %s' % t.value)
        return t

    def t_SplitPunct(self, t):
        ur'[,，。.]'
        # print(u'parsed SplitPunct word %s' % t.value)
        return t

    def t_UnsplitPunct(self, t):
        ur'[、]'
        # print(u'parsed UnsplitPunct word %s' % t.value)
        return t

    def t_WordsQuot(self, t):
        ur'[\"“](.+?)[\"”]'
        # print(u'parsed WordsQuot word %s' % t.value)
        return t

    def t_BookQuo(self, t):
        ur'《(.+?)》'
        # print(u'parsed BookQuo word %s' % t.value)
        return t

    def t_Reference(self, t):
        ur'[\[【]([0-9]+?)[\]】]'
        # print(u'parsed Reference word %s' % t.value)
        return t

    t_ignore = u" \t　"

    def t_newline(self, t):
        ur'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    # Others

    def __init__(self):
        Preprocessor.__init__(self)

    def preprocess(self, rawText, toks):
        # Build the lexer
        lexer = lex.lex(module=self, debug=False)
        # Give the lexer some input
        if isinstance(rawText, str):
            rawText = rawText.decode(encoding='utf-8')
        print(rawText)
        lexer.input(rawText)

        # Tokenize
        while True:
            tok = lexer.token()
            if not tok:
                break      # No more input
            token = Token(tok.value, tok.type)
            toks.append(token)
