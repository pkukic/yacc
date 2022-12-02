from constants import *
from LR import LR
from gen_tree import GenTree


def main():
    lr = LR(REDUCTIONS_FILE, LR_TABLE_FILE)
    c = "c 1 this is C"
    d = "d 2 this is D"
    input = [c, c, c, c, d, c, c, d]
    g_tree = lr.parse(input)
    g_tree.print()

if __name__ == '__main__':
    main()