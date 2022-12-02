from constants import *


class Leaf:

    _uniform_sign = None
    _row_number = None
    _lex_repr = None
    type = LEAF
    
    def __init__(self, str):
        temp = str.split(' ')
        self._uniform_sign = temp[0]
        if self._uniform_sign != EPSILON:
            self._row_number = temp[1]
            self._lex_repr = ' '.join(temp[2:])
    

    def print(self, depth):
        if self._uniform_sign != EPSILON:
            print((depth * " ") + self._uniform_sign + " " + self._row_number + " " + self._lex_repr)
        else:
            print((depth * " ") + "$")
    

    def get_name(self):
        return self._uniform_sign
    
    def get_line(self):
        return self._row_number
    
    def get_lex(self):
        return self._lex_repr
