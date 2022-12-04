from constants import NODE


class Node:

    _children = list()
    _unfinished_sign = None
    type = NODE


    def __init__(self, unfinished_sign, children):
        self._unfinished_sign = unfinished_sign
        self._children = children


    def print(self, depth):
        print((depth * " ") + self._unfinished_sign)
        for child in self._children:
            child.print(depth + 1)
    

    # append to the front of the list
    def add_child(self, child):
        self._children.insert(0, child)
    

    def get_name(self):
        return self._unfinished_sign
    

    def __repr__(self):
        return self._uniform_sign
    

    def __str__(self):
        return self._uniform_sign