import lex

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
    'TILDE',
    'ATOMTOK'
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
t_ATOMTOK = r'\'.*?\''
t_ignore = " \t"

def t_comment(t):
    r'\/\/[^\n]*'
    #print "Debug: handling comment..."

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
