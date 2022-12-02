from gen_tree import GenTree
from stack import Stack
from constants import *
from leaf import Leaf
from action import *
import os


class LR:

    _input = None
    _input_ptr = 0
    _sync_signs = list()
    _stack = Stack()
    _reductions_temp = list()
    _actions = list()
    _sign_encodings = dict()


    def __init__(self, reductions_file, lr_table_file):
        # read the reduction_rules_file
        with open(reductions_file, 'r') as red_file_r:
            encoded_red_rules = red_file_r.read().split(NEWLINE_DELIMITER)[:-1] # last rule will be empty -> discard it
            for encoded_rule in encoded_red_rules:
                self._reductions_temp.append(encoded_rule.split(INLINE_DELIMITER))
        

        with open(lr_table_file, 'r') as lr_table_r:
            lr_table = lr_table_r.read().split(NEWLINE_DELIMITER)[:-1] # last one will be empty -> discard it
            # first row are sync signs
            self._sync_signs = lr_table[0].split(INLINE_DELIMITER)

            # second row are signs
            for i, sign in enumerate(lr_table[1].split(INLINE_DELIMITER)):
                self._sign_encodings.update({sign: i})
            
            for state, action_row in enumerate(lr_table[2:]):
                self._actions.append([])

                for action_name in action_row.split(INLINE_DELIMITER):
                    if action_name == ACCEPT:
                        action = Accept()
                    elif action_name[0] == 's':
                        new_top_state = action_name.split('_')[1]
                        action = Put(new_top_state)
                    elif action_name[0] == 'p':
                        new_top_state = action_name.split('_')[1]
                        action = Move(new_top_state)
                    elif action_name[0] == 'r':
                        reduction_number = int(action_name.split('_')[1])
                        left_side = self._reductions_temp[reduction_number][0]
                        right_side = self._reductions_temp[reduction_number][1:]
                        action = Reduct(left_side, right_side)
                    else:
                        action = Move(REJECT)

                    self._actions[state].append(action)


    def parse(self, input) -> GenTree:
        self._input = input
        if len(self._input) == 0:
            return GenTree(None)
        
        while(self._input_ptr <= len(self._input)):
            # what is being read from the input line
            if self._input_ptr == len(self._input):
                leaf = Leaf(f'{END_OF_INPUT} 0 T')
            else:
                leaf = Leaf(self._input[self._input_ptr])
            
            # get next action based on:
            #   current state and next sign from input line
            #   current state and last sign on the stack
            if self._stack.read_from_input():
                next_in = leaf.get_name()
            else:
                next_in = self._stack.get_last_node().get_name()
            # find the action that should be done
            action_index = self._sign_encodings[next_in]
            action = self._actions[int(self._stack.get_last_state())][action_index]

            # execute action
            try:
                status = action.execute(self._stack, leaf)
                # if action is to accept return the tree
                if status == ACCEPT:
                    return GenTree(self._stack.pop_node())
                if action.move_ptr:
                    self._input_ptr += 1
            except:
                # TODO!!!!!!!!!!!!!
                # action not defined
                # OPORAVAK OD POGREŠKE
                ...