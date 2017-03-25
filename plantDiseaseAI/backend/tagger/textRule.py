#!/usr/bin/python
import sys,os
import pprint
sys.path.insert(0, "../..")

import lex
import yacc
from AST import *
import decimal

pp = pprint.PrettyPrinter(indent = 2)

keywords = ('internal')

tokens = (
    'internal',
    'SLOT',
    'LSB',
    'RSB',
    'LAB',
    'RAB',
    'LB',
    'RB',
    'QM',
    'PLUS',
    'STAR',
    'ASSIGN',
    'RQ',
    'SEMICOLON',
    'DQ',
    'NAME',
    'SPANTYPE',
    'POW',
    'AT',
    'STR',
    'COMMA',
    'COLON',
    'NOT',
    'OR',
    'AND',
    'LBRACE',
    'RBRACE',
    'DOT',
    'TILDE'
)

t_SLOT = r'#'
t_LSB = r'\['
t_RSB = r'\]'
t_LAB = r'<'
t_RAB = r'>'
t_LB = r'{'
t_RB = r'}'
t_QM = r'\?'
t_PLUS = r'\+'
t_STAR = r'\*'
t_ASSIGN = r'='
t_RQ = r'`'
t_SEMICOLON = r';'
t_DQ = r'"'
t_SPANTYPE = r'[a-zA-Z_\/]+'
t_POW = r'\^'
t_AT = r'@'
t_STR = r'".*?"'
t_COMMA = r','
t_COLON = r':'
t_NOT = r'!'
t_OR = r'\|\|'
t_AND = r'&&'
t_LBRACE = r'\('
t_RBRACE = r'\)'
t_DOT = '\.'
t_TILDE = '~'
t_ignore = " \t"

def t_comment(t):
    r'\/\/[^\n]*'
    print "Debug: handling comment..."

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print "Illegal character '%s'" % t.value[0].encode('utf-8')

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in keywords:
        t.type = t.value
    return t

context = ParseContext()

precedence = (
    ('left', 'STAR', 'PLUS', 'QM'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT')
)

def p_rules(p):
    """rules : rule
             | rules rule"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_rule(p):
    """rule : NAME ASSIGN expr
            | internal NAME ASSIGN expr"""
    if len(p) == 4:
        p[0] = Rule('public', p[1], p[3])
    elif len(p) == 5:
        p[0] = Rule('internal', p[2], p[4])
    else:
        pass

def p_expr(p):
    """expr : counted
            | counted RQ actionSeq RQ
            | counted SLOT NAME"""
    p[0] = p[1]
    if len(p) == 4:
        p[0]._annotations.extend(p[3])
    else:
        p[0]._annotations.append(Annotation('Slot', p[3], AtomCover()))

def p_actionSeq(p):
    """actionSeq : action
                 | actionSeq SEMICOLON action"""
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]

def p_action(p):
    """action : NAME ASSIGN STR"""
    p[0] = Action('General', p[1], p[3])

def p_counted(p):
    """counted : term
               | term QM
               | term STAR
               | term PLUS"""
    p[0] = p[1]
    if len(p) == 3:
        if p[2] == '?':
            p[0]._count = '\0'
        elif p[2] == '*':
            p[0]._count = '*'
        elif p[2] == '+':
            p[0]._count = '+'
        else:
            pass

def p_term(p):
    """term : matchExpr
            | orderedExprs
            | unorderedExprs
            | mirroredExprs
            | alteredExprs
            | callExpr"""
    p[0] = p[1]

def p_orderedExprs(p):
    """orderedExprs : LB exprs RB"""
    p[0] = TermSeq('ordered', p[2])

def p_unorderedExprs(p):
    """unorderedExprs : TILDE LB exprs RB"""
    p[0] = TermSeq('unordered', p[3])

def p_mirroredExprs(p):
    """mirroredExprs : POW LB exprs RB"""
    p[0] = TermSeq('mirror', p[3])

def p_alteredExprs(p):
    """alteredExprs : LSB exprs RSB"""
    p[0] = TermSeq('altered', p[2])

def p_callExpr(p):
    """callExpr : AT NAME"""
    p[0] = Call(p[2], "")

def p_exprs(p):
    """exprs : expr
             | exprs expr"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_span(p):
    """span : SPANTYPE
            | COLON spanAttr
            | SPANTYPE COLON spanAttr"""
    if len(p) == 2:
        p[0] = Span(p[1], "", "")
    elif len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = p[3]
        p[0]._type = p[1]

# attr_key | attr_key = "attr_value"
def p_spanAttr(p):
    """spanAttr : NAME
                | NAME ASSIGN STR"""
    if len(p) == 2:
        p[0] = Span("", p[1], "")
    else:
        p[0] = Span("", p[1], p[2])

def p_exprDot(p):
    """exprDot : DOT
               | LAB RAB"""
    p[0] = Atom()

def p_exprToken(p):
    """exprToken : STR"""
    print "debug: " + p[1]
    p[0] = TokenValue(p[1])

def p_exprSpan(p):
    """exprSpan : LAB span RAB"""
    p[0] = p[2]

def p_exprOperation(p):
    """exprOperation : NOT matchExpr
                     | matchExpr AND matchExpr
                     | matchExpr OR matchExpr"""
    if len(p) == 3:
        p[0] = UnaryOpNode(p[1], p[2])
    else:
        p[0] = BinaryOpNode(p[2], p[1], p[3])

def p_matchExpr(p):
    """matchExpr : exprDot
                 | exprToken
                 | exprSpan
                 | exprOperation
                 | LBRACE matchExpr RBRACE"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

if __name__ == '__main__': 
    filename = sys.argv[1]
    with open(filename, 'r') as fd:
        data = fd.read().decode('utf-8')
        lexer = lex.lex(debug=1, optimize=0,
                                lextab='lextab', reflags=0)
        lexer.input(data)

        for tok in iter(lexer.token, None):
            if not tok:
                break
            sys.stdout.write('(%s,%r,%d,%d)\n' % (tok.type, tok.value, tok.lineno, tok.lexpos))

        #parser = yacc.yacc()
        #result = parser.parse(lexer=lexer)
        #ast = AST(result)
        #ast.dumpAST()
        #pp.pprint(result)
