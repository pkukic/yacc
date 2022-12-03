import itertools
import pprint
import copy

TOCKA = '<*>'
EOS = '#'

class LR_stavka:
    def __init__(self, prod, T_set):
        self.prod = prod
        self.T_set = T_set

    def update_T_set(self, new_T_set):
        self.T_set = new_T_set

    def __eq__(self, other):
        return isinstance(other, type(self)) and \
             self.prod == other.prod and \
             self.T_set == other.T_set

    def __hash__(self) -> int:
        return hash((self.prod, self.T_set))

    def __repr__(self):
        s = ''
        s += f"(P: {self.prod}, T: {self.T_set})"
        return s


class Grammar:
    def __init__(self, nonterm_chars, term_chars, syn_chars, productions, first_nonterm_char):
        self.nonterm_chars = nonterm_chars
        self.term_chars = term_chars
        self.all_chars = []
        self.syn_chars = syn_chars
        self.productions = productions
        self.first_nonterm_char = first_nonterm_char
        self.empty_chars = []

        self.zapocinje_izravno_znakom = []
        self.zapocinje_znakom = []
        self.zapocinje = {}

        self.lr_stavke = []
        self.visited_stavke = []

        self.enka_transitions = {}

    def calculate_all_chars(self):
        self.all_chars = self.nonterm_chars + self.term_chars

    def calculate_zapocinje(self):
        ind_with_all = list(enumerate(self.all_chars))
        ind_with_term = []
   
        for pair in ind_with_all:
            if pair[1] in self.term_chars:
                ind_with_term.append(pair)

        for pair in ind_with_all:
            self.zapocinje[pair[1]] = [termpair[1] for termpair in ind_with_term if self.zapocinje_znakom[pair[0]][termpair[0]]]

        return

    def calculate_lr_stavke(self):
        lr_stavke = []
        for prod in self.productions:
            if prod[1] == '':
                prod_new = (prod[0], TOCKA)
                lr_stavke.append(LR_stavka(prod_new, ()))
            else:
                elems = prod[1].split(' ')
                for i in range(len(elems)):
                    prod_new = (prod[0], ' '.join(elems[:i] + [TOCKA] + elems[i:]))
                    lr_stavke.append(LR_stavka(prod_new, ()))
                lr_stavke.append(LR_stavka((prod[0], ' '.join(elems + [TOCKA])), ()))
        self.lr_stavke = lr_stavke


    def move_dot(rhs_as_list):
        new_rhs = copy.deepcopy(rhs_as_list)
        dot_pos = new_rhs.index(TOCKA)
        new_rhs[dot_pos], new_rhs[dot_pos + 1] = new_rhs[dot_pos + 1], new_rhs[dot_pos]
        return new_rhs

    def find_first_nonempty_char(self, rhs_as_list):
        for char in rhs_as_list:
            if char not in self.empty_chars:
                return char
        return None


    # This thing takes in start_state and outputs a list of next_states
    # (with calculated T_set)
    def possible_transitions(self, start_lr_stavka):
        lhs, rhs = start_lr_stavka.prod
        T_start = start_lr_stavka.T_set

        rhs_split = rhs.split(' ')
        dot_pos = rhs_split.index(TOCKA)

        # if the dot is the last character in the RHS, nothing can be generated
        if dot_pos == len(rhs_split) - 1:
            return []

        char_after_dot = rhs_split[dot_pos + 1]
        transition_char = char_after_dot
        moved_dot_state = LR_stavka(prod=(lhs, ' '.join(Grammar.move_dot(rhs_split))), T_set=T_start)
        without_eps_transition = [(transition_char, moved_dot_state)]

        if char_after_dot in self.term_chars:
            return without_eps_transition
    
        # find all lr stavke where lhs == char_after_dot
        new_lr_stavke = [copy.deepcopy(lr) for lr in self.lr_stavke if lr.prod[0] == char_after_dot and \
             lr.prod[1].startswith(TOCKA)]

        # construct new T_set

        eps_transitions = []
        
        # if the character after the dot is the last one,
        if dot_pos + 1 == len(rhs_split) - 1:
            # beta doesn't exist
            # that means new set is equal to old set
            new_T_set = T_start
            for stavka in new_lr_stavke:
                stavka.update_T_set(new_T_set)
                eps_transitions = [('', stavka) for stavka in new_lr_stavke]
            
            return without_eps_transition + eps_transitions

        # otherwise, beta does exist
        # if all characters in beta are empty,
        # that means that epsilon can be generated from beta
        new_T_set = tuple()
        beta = rhs_split[dot_pos + 2:]
        if all([x in self.empty_chars for x in beta]):
            # so count in the old T set
            new_T_set += T_start

        first_zapocinje = tuple()
        for char in beta:
            if len(self.zapocinje[char]) > 0:
                first_zapocinje = tuple(self.zapocinje[char])
        
        new_T_set += first_zapocinje
        new_T_set = tuple(set(new_T_set))

        for stavka in new_lr_stavke:
            stavka.update_T_set(new_T_set)

        eps_transitions = [('', stavka) for stavka in new_lr_stavke]

        return without_eps_transition + eps_transitions


    def calculate_enka_transitions(self):
        start_state = copy.deepcopy(self.lr_stavke[0])
        start_state.update_T_set(tuple('#'))
        stack_LR_stavke = [start_state]
        self.visited_stavke.append(start_state)
        
        while len(stack_LR_stavke) > 0:

            print(stack_LR_stavke)

            for stavka in stack_LR_stavke:  

                # get all possible transitions  
                transitions = self.possible_transitions(stavka)

                pprint.pprint(transitions)
                
                for char, new_stavka in transitions:
                
                    if new_stavka not in self.visited_stavke:
                        print(new_stavka)
                        self.visited_stavke.append(new_stavka)
                        stack_LR_stavke.append(new_stavka)
                    
                    self.enka_transitions.setdefault((stavka, char), []).append(new_stavka)

                stack_LR_stavke.remove(stavka)
        return


    def __repr__(self):
        s = ''
        s += f"NT: {self.nonterm_chars}" + "\n"
        s += f"First NT: {self.first_nonterm_char}" + "\n"
        s += f"T: {self.term_chars}" + "\n"
        s += f"All: {self.all_chars}" + "\n"
        s += f"Syn: {self.syn_chars}" + "\n"
        s += "Prod:\n"
        s += pprint.pformat(self.productions) + "\n"
        s += f"Empty chars: {self.empty_chars}" + "\n"
        s += "ZapocinjeIzravnoZnakom:\n"
        s += pprint.pformat(self.zapocinje_izravno_znakom) + "\n"
        s += "ZapocinjeZnakom:\n"
        s += pprint.pformat(self.zapocinje_znakom) + "\n"
        s += "Zapocinje:\n"
        s += pprint.pformat(self.zapocinje) + "\n"
        s += "LR stavke:\n"
        s += pprint.pformat(self.lr_stavke) + "\n"
        s += 'ENKA transitions:\n'
        s += pprint.pformat(self.enka_transitions) + "\n"
        s += "------------------------------"
        return s



def split_ignore_first(s):
    return s.split(' ')[1:]

def parse(filestring):
    as_lines = filestring.splitlines()
    # %V
    nonterm_chars = split_ignore_first(as_lines[0])
    # %T
    term_chars = split_ignore_first(as_lines[1])
    # %Syn
    syn_chars = split_ignore_first(as_lines[2])

    # print('NT: ', nonterm_chars)
    # print('T: ', term_chars)
    # print('Syn: ', syn_chars)
    
    productions = as_lines[3:]
    
    parsed_productions = []
    prev_lhs = ''

    first_nonterm_char = nonterm_chars[0]

    for line in productions:
        if not line.startswith(' '):
            prev_lhs = line
            continue
        else:
            # ignoring the case when first line is <space>b or something
            # replace $ (epsilon) with '' (nothing)
            rhs = line.lstrip()
            rhs = rhs.replace('$', '')
            parsed_productions.append((prev_lhs, rhs))
    
    # print('Prod: ', parsed_productions)

    return Grammar(nonterm_chars=nonterm_chars, term_chars=term_chars, syn_chars=syn_chars, productions=parsed_productions, first_nonterm_char=first_nonterm_char)


def add_first_prod(g):
    g.nonterm_chars.insert(0, '<%>')
    g.productions.insert(0, ('<%>', g.first_nonterm_char))
    g.first_nonterm_char = '<%>'
    g.calculate_all_chars()
    return


def find_empty_nonterm_chars(g):
    all_empty_chars = []
    new_empty_chars = []
    previous_empty_chars = []
    
    for prod in g.productions:
        if prod[1] == '':
            new_empty_chars.append(prod[0])
    
    while len(new_empty_chars) != 0:
        # print(new_empty_chars)
        all_empty_chars.extend(new_empty_chars)
        previous_empty_chars = new_empty_chars
        new_empty_chars = []

        for prod in g.productions:
            # print(prod)
            if prod[1] in previous_empty_chars:
                # print(prod)
                new_empty_chars.append(prod[0])
    
    return all_empty_chars


def isDirectProduction(prod, B, g):
    _, rhs = prod
    rhs = rhs.split(' ')

    if rhs[0] == B:
        return True
    
    try:
        ind = rhs.index(B)
    except ValueError:
        return False
    
    sublist = rhs[:ind]
    if all([item in g.empty_chars for item in sublist]):
        return True
    
    return False

def zapocinje_izravno_znakom(A, B, g):
    if A == B:
        return True
    
    prods_from_A = [prod for prod in g.productions if prod[0] == A]
    return any([isDirectProduction(prod, B, g) for prod in prods_from_A])


def make_zapocinje_izravno_matrix(g):
    all_chars = g.all_chars
    all_indices = list(range(len(all_chars)))
    m = [[0 for i in range(len(all_chars))] for j in range(len(all_chars))]
    pairs = list(itertools.product(all_chars, all_chars))
    indices_pairs = list(itertools.product(all_indices, all_indices))
    # print(pairs)
    # print(indices_pairs)
    
    # i is also used for indexing through indices_pairs
    for i in range(len(pairs)):
        pair_i = pairs[i]
        indices_i = indices_pairs[i]

        # print(pair_i, indices_i)
        m[indices_i[0]][indices_i[1]] = int(zapocinje_izravno_znakom(pair_i[0], pair_i[1], g))
    
    return m

# https://stackoverflow.com/questions/22519680/warshalls-algorithm-for-transitive-closurepython
def warshall_transitive_closure(g):
    zapocinje_izravno_znakom = g.zapocinje_izravno_znakom
    zapocinje_znakom = copy.deepcopy(zapocinje_izravno_znakom)
    n = len(zapocinje_izravno_znakom)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                zapocinje_znakom[i][j] = zapocinje_znakom[i][j] or \
                (zapocinje_znakom[i][k] and zapocinje_znakom[k][j])
    return zapocinje_znakom


def main():
    fname = './san_files/minusLang.san'
    with open(fname, 'r') as file:
        filestring = file.read()
   
    g = parse(filestring)
    print(g)
    add_first_prod(g)
    print(g)
    empty_chars = find_empty_nonterm_chars(g)
    g.empty_chars = empty_chars
    print(g)
    m = make_zapocinje_izravno_matrix(g)
    g.zapocinje_izravno_znakom = m
    print(g)
    w = warshall_transitive_closure(g)
    g.zapocinje_znakom = w
    print(g)
    g.calculate_zapocinje()
    print(g)
    g.calculate_lr_stavke()
    print(g)
    g.calculate_enka_transitions()
    print(g)
    
    

if __name__ == '__main__':
    main()

