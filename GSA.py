import itertools
import pprint
import copy
import sys
import os

import analizator.constants as constants

TOCKA = '<*>'
EOS = '#'
FNT = '<%>'
EPS = '$'

def find_key_for_value(d, val):
    for key, v in d.items():
        if v == val:
            return key
    return None

def get_analizator_dir():
    # get the right path to the files
    analizator_dir = os.path.abspath(os.getcwd())
    if not analizator_dir.endswith('analizator') and not analizator_dir.endswith('analizator' + os.sep):
        analizator_dir = os.path.join(analizator_dir, 'analizator')
    return analizator_dir

def split_ignore_first(s):
    return s.split(' ')[1:]

class DKA_State:
    def __init__(self, state_id, stavke_tup):
        self.state_id = state_id
        self.stavke_tup = stavke_tup

    def update_id(self, new_id):
        self.state_id = new_id

    # def __eq__(self, other):
    #     return isinstance(other, type(self)) and \
    #         set(self.stavke_tup) == set(other.stavke_tup)

    def __hash__(self):
        return sum([hash(t) for t in self.stavke_tup])

    def __repr__(self):
        s = ''
        s += f'(StateID: {self.state_id}, '
        s += pprint.pformat(self.stavke_tup) + ")"
        return s


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

    def __hash__(self):
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
        self.lr_stavke_with_T_sets = []

        self.visited_dka = []
        self.dka_transitions = {}

        self.pomakni_lr = []
        self.prihvati_lr = ''
        self.reduciraj_lr = []

        self.novostanje = []
        self.akcija = []

        self.lr_table_string = ''
        self.redukcije_string = ''

    def add_first_prod(self):
        self.nonterm_chars.insert(0, FNT)
        self.productions.insert(0, (FNT, self.first_nonterm_char))
        self.first_nonterm_char = FNT
        self.calculate_all_chars()
        return

    def find_empty_nonterm_chars(self):
        all_empty_chars = []
        new_empty_chars = []
        previous_empty_chars = []
        
        for prod in self.productions:
            if prod[1] == '':
                new_empty_chars.append(prod[0])
        
        while len(new_empty_chars) != 0:
            # print(new_empty_chars)
            all_empty_chars.extend(new_empty_chars)
            previous_empty_chars = new_empty_chars
            new_empty_chars = []

            for prod in self.productions:
                # print(prod)
                if prod[1] in previous_empty_chars:
                    # print(prod)
                    new_empty_chars.append(prod[0])

        self.empty_chars = all_empty_chars
        return
    
    def isDirectProduction(self, prod, B):
        _, rhs = prod
        rhs = rhs.split(' ')

        if rhs[0] == B:
            return True
        
        try:
            ind = rhs.index(B)
        except ValueError:
            return False
        
        sublist = rhs[:ind]
        if all([item in self.empty_chars for item in sublist]):
            return True
        
        return False

    def zapocinje_izravno_znakom_f(self, A, B):
        if A == B:
            return True
        
        prods_from_A = [prod for prod in self.productions if prod[0] == A]
        return any([self.isDirectProduction(prod, B) for prod in prods_from_A])


    # https://stackoverflow.com/questions/22519680/warshalls-algorithm-for-transitive-closurepython
    def warshall_transitive_closure(self):
        zapocinje_izravno_znakom = self.zapocinje_izravno_znakom
        zapocinje_znakom = copy.deepcopy(zapocinje_izravno_znakom)
        n = len(zapocinje_izravno_znakom)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    zapocinje_znakom[i][j] = zapocinje_znakom[i][j] or \
                    (zapocinje_znakom[i][k] and zapocinje_znakom[k][j])
        self.zapocinje_znakom = zapocinje_znakom
        return

    def make_zapocinje_izravno_matrix(self):
        all_chars = self.all_chars
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
            m[indices_i[0]][indices_i[1]] = int(self.zapocinje_izravno_znakom_f(pair_i[0], pair_i[1]))
        
        self.zapocinje_izravno_znakom = m
        return

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

    @staticmethod
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

        # print(f'beta: {beta}')

        if all([x in self.empty_chars for x in beta]):
            # so count in the old T set
            new_T_set += T_start

        first_zapocinje = tuple()
        i = 0
        for char in beta:
            if len(self.zapocinje[char]) > 0 and char in self.empty_chars:
                first_zapocinje += tuple(self.zapocinje[char])
                i += 1
            else:
                break
        
        # print(f'i, {i}')
        if i <= len(beta) - 1 and beta[i] not in self.empty_chars:
            first_zapocinje += tuple(self.zapocinje[beta[i]])
        else:
            first_zapocinje += tuple()
        

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

            # print(stack_LR_stavke)

            for stavka in stack_LR_stavke:

                # print(f'trenutno stanje: {stavka}')

                # get all possible transitions  
                transitions = self.possible_transitions(stavka)

                # pprint.pprint(transitions)

                # print(f'prijelazi prema:')
                # pprint.pprint(transitions)
                
                for char, new_stavka in transitions:
                
                    if new_stavka not in self.visited_stavke:
                        # print(new_stavka)
                        self.visited_stavke.append(new_stavka)
                        stack_LR_stavke.append(new_stavka)
                    
                    self.enka_transitions.setdefault((stavka, char), []).append(new_stavka)

                stack_LR_stavke.remove(stavka)
        return

    def calculate_lr_stavke_with_T_sets(self):
        for k, vals in self.enka_transitions.items():
            stavka, trans = k
            if stavka not in self.lr_stavke_with_T_sets:
                self.lr_stavke_with_T_sets.append(stavka)
            for v in vals:
                if v not in self.lr_stavke_with_T_sets:
                    self.lr_stavke_with_T_sets.append(v)
        # print(f'lrtsets, {len(self.lr_stavke_with_T_sets)}')
        return

    def epsilon_closure(self, stavka):
        new_stavka = copy.deepcopy(stavka)
        stavke_stack = copy.deepcopy(self.enka_transitions.setdefault((new_stavka, ''), []))
        visited = set([new_stavka] + stavke_stack)
        while len(stavke_stack) > 0:
            new = stavke_stack.pop(0)
            neighbours = self.enka_transitions.setdefault((new, ''), [])
            for n in neighbours:
                if n not in visited:
                    stavke_stack.append(n)
                    visited.add(n)
        return visited

    def epsilon_closure_for_list(self, l):
        ec_set = set()
        for stavka in l:
            ec_set |= self.epsilon_closure(stavka)
        return list(ec_set)

    def enka_to_dka(self):
        hd = {}
        stack = []
        transitions = {}
        state_counter = 0
        stavka_0 = self.lr_stavke_with_T_sets[0]
        # ovo je lista
        state_0_stavke = self.epsilon_closure_for_list([stavka_0])
        first_state = DKA_State(0, tuple(state_0_stavke))
        hd.update({hash(first_state): first_state})
        stack.append(first_state)
        while len(stack) > 0:
            current_state = stack.pop(0)
            for char in self.all_chars:
                new_stavke = []
                for stavka in current_state.stavke_tup:
                    lijeva_strana = stavka.prod[0]
                    desna_strana = stavka.prod[1].split(' ')
                    T_set = stavka.T_set
                    tocka_index = desna_strana.index(TOCKA)
                    
                    if tocka_index == len(desna_strana) - 1:
                        continue

                    if desna_strana[tocka_index + 1] == char:
                        nova_desna_strana = Grammar.move_dot(desna_strana)
                        nova_stavka = LR_stavka((lijeva_strana, ' '.join(nova_desna_strana)), tuple(T_set))
                        new_stavke.append(nova_stavka) 
                
                potential_new_state_productions = self.epsilon_closure_for_list(new_stavke)
                potential_new_state = DKA_State(0, tuple(potential_new_state_productions))

                if len(new_stavke) == 0:
                    continue
                
                key = hash(potential_new_state)
                if key in hd:
                    transitions.update({(current_state, char): hd[key]})
                else:
                    state_counter += 1
                    potential_new_state.update_id(state_counter)
                    hd.update({key: potential_new_state})
                    transitions.update({(current_state, char): potential_new_state})
                    stack.append(potential_new_state)
        self.dka_transitions = transitions
        self.visited_dka = list(hd.values())
        return


    def get_all_pomakni(self):
        self.pomakni_lr = [s for s in self.lr_stavke if s.prod[1].split(' ')[-1] != TOCKA]
        return

    def get_all_redukcije(self):
        self.reduciraj_lr = [s for s in self.lr_stavke if s.prod[1].split(' ')[-1] == TOCKA and not (s.prod[0] == FNT and s.prod[1].split(' ')[-1] == TOCKA)]
        return

    def get_prihvati(self):
        self.prihvati_lr = [s for s in self.lr_stavke if s.prod[0] == FNT and s.prod[1].split(' ')[-1] == TOCKA][0]
        return

    def distribute_lr(self):
        self.get_all_pomakni()
        self.get_all_redukcije()
        self.get_prihvati()
        return

    def calc_novostanje(self):
        # print('calc_novostanje')
        for i in range(len(self.visited_dka)):
            self.novostanje.append([])
            for j in range(len(self.nonterm_chars)):
                self.novostanje[i].append(None) 
        # self.novostanje = [[None] * len(self.nonterm_chars)] * len(self.visited_dka)
        # pprint.pprint(self.novostanje)
        for key in self.dka_transitions:
            if key[1] in self.nonterm_chars:
                start_id = key[0].state_id
                char = key[1]
                char_ind = self.nonterm_chars.index(char)
                new_state = self.dka_transitions[key].state_id
                # print(start_id, char, char_ind, new_state)
                self.novostanje[start_id][char_ind] = f's_{new_state}'
        # pprint.pprint(self.novostanje)
        for i in range(len(self.novostanje)):
            for j in range(len(self.novostanje[0])):
                if self.novostanje[i][j] is None:
                    self.novostanje[i][j] = 'x'
        return

    def calc_akcija(self):
        self.term_chars.append('#')
        for i in range(len(self.visited_dka)):
            self.akcija.append([])
            for j in range(len(self.term_chars)):
                self.akcija[i].append(None)
        
        for s in self.visited_dka:
            for t in sorted(s.stavke_tup, key=lambda x: self.lr_stavke.index(LR_stavka(x.prod, tuple())), reverse=True):
                for i, r in reversed(list(enumerate(self.reduciraj_lr))):
                    if t.prod == r.prod:
                        chars = t.T_set
                        for c in chars:
                            self.akcija[s.state_id][self.term_chars.index(c)] = f'r_{i}'
            
            for ss in s.stavke_tup:
                lhs, rhs = ss.prod
                t_set = ss.T_set
                if lhs == FNT and rhs.endswith(TOCKA) and t_set == (EOS,):
                    self.akcija[s.state_id][self.term_chars.index(EOS)] = constants.ACCEPT
                for p in self.pomakni_lr:
                    rhs_split = p.prod[1].split(' ')
                    char_after_dot = rhs_split[rhs_split.index(TOCKA) + 1]
                    if char_after_dot not in self.term_chars:
                        continue
                    if p.prod == ss.prod:
                        for key in self.dka_transitions:
                            if key[1] == char_after_dot and key[0].state_id == s.state_id:
                                self.akcija[s.state_id][self.term_chars.index(char_after_dot)] = f'p_{self.dka_transitions[key].state_id}'
        
        for i in range(len(self.akcija)):
            for j in range(len(self.akcija[0])):
                if self.akcija[i][j] is None:
                    self.akcija[i][j] = 'x'

        return


    def make_reductions_string(self):
        reductions = self.reduciraj_lr
        self.redukcije_string = constants.NEWLINE_DELIMITER.join([(r.prod[0] + ' ' + (r.prod[1] if r.prod[1] != TOCKA else constants.EPSILON)).replace(TOCKA, '').rstrip()
                                .replace(' ', constants.INLINE_DELIMITER) for r in reductions]) + \
                                     constants.NEWLINE_DELIMITER
        return
    
    def make_lr_table_string(self):
        fs = ''
        syn_indices = [str(self.term_chars.index(s)) for s in self.syn_chars]
        fs += constants.INLINE_DELIMITER.join(syn_indices) + constants.NEWLINE_DELIMITER
        fs += constants.INLINE_DELIMITER.join(self.term_chars + self.nonterm_chars[1:]).replace(EOS, constants.END_OF_INPUT) + constants.NEWLINE_DELIMITER
        akcija_and_novostanje = []
        # #print(self)
        for i in range(len(self.akcija)):
            akcija_and_novostanje.append(self.akcija[i] + self.novostanje[i][1:])
        for row in akcija_and_novostanje:
            fs += constants.INLINE_DELIMITER.join(row) + constants.NEWLINE_DELIMITER
        self.lr_table_string = fs
        return
    
    def write_to_files(self):
        lr_table_fname = os.path.join(get_analizator_dir(), 'LR_table.txt')
        reductions_fname = os.path.join(get_analizator_dir(), 'reductions.txt')

        with open(lr_table_fname, 'w+') as lrf:
            lrf.write(self.lr_table_string)
    
        with open(reductions_fname, 'w+') as rf:
            rf.write(self.redukcije_string)
        
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
        s += "LR stavke with T sets:\n"
        s += pprint.pformat(self.lr_stavke_with_T_sets) + "\n"
        s += "DKA visited:\n"
        s += pprint.pformat(self.visited_dka) + "\n"
        s += "DKA transitions:\n"
        for key in self.dka_transitions:
            s += f"{key[0].state_id} {key[1]} {self.dka_transitions[key].state_id}\n"
        s += "Prihvati stavka:\n"
        s += str(self.prihvati_lr) + "\n"
        s += "Reduciraj stavke:\n"
        s += pprint.pformat(self.reduciraj_lr) + "\n"
        s += "Pomakni stavke:\n"
        s += pprint.pformat(self.pomakni_lr) + "\n"
        s += "NovoStanje:\n"
        s += pprint.pformat(self.novostanje) + "\n"
        s += "Akcija:\n"
        s += pprint.pformat(self.akcija) + "\n"
        s += "Redukcije string:\n"
        s += self.redukcije_string + "\n"
        s += "LR table string:\n"
        s += self.lr_table_string + "\n"
        s += "------------------------------"
        return s

    def run(self):
        self.add_first_prod()
        # print(self)
        self.find_empty_nonterm_chars()
        # print(self)
        self.make_zapocinje_izravno_matrix()
        # print(self)
        self.warshall_transitive_closure()
        # print(self)
        self.calculate_zapocinje()
        # print(self)
        self.calculate_lr_stavke()
        # print(self)
        self.calculate_enka_transitions()
        # print(self)
        self.calculate_lr_stavke_with_T_sets()
        # print(self)
        self.enka_to_dka()
        # print(self)
        self.distribute_lr()
        # print(self)
        self.calc_novostanje()
        # print(self)
        self.calc_akcija()
        # print(self)
        self.make_lr_table_string()
        self.make_reductions_string()
        self.write_to_files()
        # print(self)
        return

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
            rhs = rhs.replace(EPS, '')
            parsed_productions.append((prev_lhs, rhs))
    
    # print('Prod: ', parsed_productions)

    return Grammar(nonterm_chars=nonterm_chars, term_chars=term_chars, syn_chars=syn_chars, productions=parsed_productions, first_nonterm_char=first_nonterm_char)


def main():
    input = '\n'.join([line.rstrip() for line in sys.stdin.readlines()])
    g = parse(input)
    g.run()

    # fname = './san_files/kanon_gramatika.san'
    # with open(fname, 'r') as file:
    #     filestring = file.read()
   
   
if __name__ == '__main__':
    main()

