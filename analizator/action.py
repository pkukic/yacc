from constants import *
from leaf import Leaf
from stack import Stack
from node import Node


class Action:
    
    type = None
    move_ptr = None

    def execute(self, stack: Stack, leaf: Leaf):
        ...


class Move(Action):

    _new_top_state = None
    
    def __init__(self, new_top_state):
        self.move_ptr = True
        self._new_top_state = new_top_state
        self.type = MOVE
    

    def execute(self, stack: Stack, leaf: Leaf):
        # node in this case will be a Leaf object
        stack.add_state(self._new_top_state)
        stack.add_node(leaf)
        return self.type


class Reject(Action):
    
    def __init__(self):
        self.move_ptr = False
        self.type = REJECT
    

    def execute(self, stack: Stack, leaf: Leaf):
        raise Exception("Reject this")


class Put(Action):
    
    _new_top_state = None

    def __init__(self, new_top_state):
        self.move_ptr = False
        self.type = PUT
        self._new_top_state = new_top_state
    

    def execute(self, stack: Stack, leaf: Leaf):
        # node in this case will be a Node object
        stack.add_state(self._new_top_state)
        return self.type    


class Reduct(Action):

    _left_side = None
    _right_side = None    

    def __init__(self, left_side, right_side):
        self.move_ptr = False
        self.type = REDUCT
        self._left_side = left_side
        self._right_side = right_side
    

    def execute(self, stack: Stack, leaf: Leaf):
        new_node = Node(self._left_side, [])
        # special case of epsilon production
        if self._right_side == [EPSILON]:
            new_node.add_child(Leaf(f'{EPSILON} 0 $'))
        else:
            for sign in reversed(self._right_side):
                stack.pop_state()
                child = stack.pop_node()
                new_node.add_child(child)
        stack.add_node(new_node)
        return self.type


class Accept(Action):
    
    def __init__(self):
        self.move_ptr = False
        self.type = ACCEPT
    

    def execute(self, stack: Stack, leaf: Leaf):
        return self.type