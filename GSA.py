
class Grammar:
    def __init__(self, nonterm_chars, term_chars, syn_chars, productions):
        self.nonterm_chars = nonterm_chars
        self.term_chars = term_chars
        self.syn_chars = syn_chars
        self.productions = productions

    def __repr__(self):
        s = ''
        s += f"NT: {self.nonterm_chars}" + "\n"
        s += f"T: {self.term_chars}" + "\n"
        s += f"Syn: {self.syn_chars}" + "\n"
        s += f"Prod: {self.productions}"
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

    return Grammar(nonterm_chars=nonterm_chars, term_chars=term_chars, syn_chars=syn_chars, productions=parsed_productions)





def main():
    fname = './san_files/minusLang.san'
    with open(fname, 'r') as file:
        filestring = file.read()
        g = parse(filestring)
        print(g)



if __name__ == '__main__':
    main()

