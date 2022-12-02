from gen_tree import GenTree
from stack import Stack
from constants import *
from leaf import Leaf
from action import *


class LR:

    _input = None
    _input_ptr = 0
    _sync_signs = dict()
    _signs = list()
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
            for sync_sign_index in lr_table[0].split(INLINE_DELIMITER):
                if sync_sign_index != '':
                    self._sync_signs.update({int(sync_sign_index): []})

            # second row are signs
            for i, sign in enumerate(lr_table[1].split(INLINE_DELIMITER)):
                self._sign_encodings.update({sign: i})
                self._signs.append(sign)
            
            for state, action_row in enumerate(lr_table[2:]):
                self._actions.append([])

                for sign_index, action_name in enumerate(action_row.split(INLINE_DELIMITER)):
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
                        action = Reject()
                    
                    # add states for which the sync_sign has a valid action
                    if type(action) != Reject and sign_index in self._sync_signs.keys():
                        self._sync_signs[sign_index].append(state)

                    self._actions[state].append(action)


    def parse(self, input) -> GenTree:
        self._input = input
        if len(self._input) == 0:
            return GenTree(None)
        
        while(self._input_ptr <= len(self._input)):
            # what is being read from the input line
            if self._input_ptr == len(self._input):
                leaf = Leaf(f'{END_OF_INPUT} end_of_file T')
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
                # action not defined
                # error recovery
                print("*****************")
                print("[SYNTAX ERROR]")
                print(f"line: {leaf.get_line()}")
                print(f"expected uniform signs: {self.get_expected_uniform_signs()}")
                print(f"instead got uniform sign: {leaf.get_name()}, lex: {leaf.get_lex()}")
                print("*****************")
                error_recovery_status = self._recover_from_error()
                if not error_recovery_status:
                    print("FATAL, could not recover!")
                    return GenTree(None)
    

    def _recover_from_error(self):
        if self._input_ptr >= len(self._input):
            return False
            
        for i in range(self._input_ptr, len(self._input)):
            leaf = Leaf(self._input[i])
            sign_index = self._sign_encodings[leaf.get_name()]

            # the current sign is a sync sign
            if sign_index in self._sync_signs.keys():
                # remove states and corresponding nodes until a state with a defined action for the sync sign is found
                while len(self._stack.states_stack) > 0:
                    # state on the stack top has a defined action for the sync sign in input
                    if self._stack.get_last_state() in self._sync_signs[sign_index]:
                        # set input_ptr to point at the sync sign
                        # return True for success
                        self._input_ptr = i
                        return True
                    if len(self._stack.node_stack) > 0:
                        self._stack.pop_node()
                    self._stack.pop_state()
                
                break
        
        return False
    

    def get_expected_uniform_signs(self):
        expected = []
        for i, action in enumerate(self._actions[int(self._stack.get_last_state())]):
            if type(action) != Put and type(action) != Reject:
                expected.append(self._signs[i])
        return expected
