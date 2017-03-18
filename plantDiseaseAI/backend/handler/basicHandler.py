# -*- coding: utf-8 -*-
from nlu import *
from nlr import *

import pprint

pp = pprint.PrettyPrinter(indent = 2)

# A basic Handler should be able to handle the interface of
#    the understanding 
#    the ACK reply
#    ask the question of state
#    handle the branch logic
#    reset the state

class BasicHandler(object):
    def __init__(self):
        pass
    def understanding(self, 
