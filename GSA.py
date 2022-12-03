import itertools
import pprint
import copy

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

    def __repr__(self):
        s = ''
        s += f"NT: {self.nonterm_chars}" + "\n"
        s += f"First NT: {self.first_nonterm_char}" + "\n"
        s += f"T: {self.term_chars}" + "\n"
        s += f"All: {self.all_chars}" + "\n"
        s += f"Syn: {self.syn_chars}" + "\n"
        s += f"Prod: {self.productions}" + "\n"
        s += f"Empty chars: {self.empty_chars}" + "\n"
        s += "ZapocinjeIzravnoZnakom:\n"
        s += pprint.pformat(self.zapocinje_izravno_znakom) + "\n"
        s += "ZapocinjeZnakom:\n"
        s += pprint.pformat(self.zapocinje_znakom) + "\n"
        s += "Zapocinje:\n"
        s += pprint.pformat(self.zapocinje) + "\n"
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
    

if __name__ == '__main__':
    main()

