from leaf import Leaf
from node import Node


class Stack:
    
    states_stack = ['0']
    node_stack = list()


    def __init__(self):
        ...
    

    def add_state(self, state):
        self.states_stack.append(state)
    

    def pop_state(self):
        return self.states_stack.pop()
    

    def get_last_state(self):
        return self.states_stack[-1]
    

    def add_node(self, node):
        self.node_stack.append(node)
    

    def pop_node(self):
        return self.node_stack.pop()
    

    def get_last_node(self):
        return self.node_stack[-1]
    

    def read_from_input(self):
        return len(self.states_stack) == len(self.node_stack) + 1
