from constants import *


class Leaf:

    _uniform_sign = None
    _row_number = None
    _lex_repr = None
    type = LEAF

    def __init__(self, uniform_sign, row_number, lex_repr):
        self._uniform_sign = uniform_sign
        if self._uniform_sign != EPSILON:
            self._row_number = row_number
            self._lex_repr = lex_repr
    

    def __init__(self, str):
        temp = str.split(' ')
        self._uniform_sign = temp[0]
        if self._uniform_sign != EPSILON and self._uniform_sign != END_OF_INPUT:
            self._row_number = temp[1]
            self._lex_repr = ' '.join(temp[2:])
    

    def print(self, depth):
        if self._uniform_sign != EPSILON:
            print((depth * " ") + self._uniform_sign + " " + self._row_number + " " + self._lex_repr)
        else:
            print((depth * " ") + "$")
    

    def get_name(self):
        return self._uniform_sign
