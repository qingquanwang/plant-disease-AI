import yacc
from AST import *
import pprint
import sys,os

pp = pprint.PrettyPrinter(indent = 2)

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
    if len(p) == 5:
        p[0]._actions.extend(p[3])
    elif len(p) == 4:
        p[0]._actions.append(Action('Slot', p[3], AtomCover()))
    else:
        pass

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
            p[0]._count = '?'
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
    p[0] = ExprTree(p[1])

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
        p[0] = Span("", p[1], p[3])

def p_exprDot(p):
    """exprDot : DOT
               | LAB RAB"""
    p[0] = ExprTree(Atom())

def p_exprToken(p):
    """exprToken : STR"""
    #print "debug: " + p[1]
    p[0] = ExprTree(TokenValue(p[1]))

def p_exprSpan(p):
    """exprSpan : LAB span RAB"""
    p[0] = ExprTree(p[2])

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

