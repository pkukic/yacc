from constants import *
from LR import LR
from gen_tree import GenTree


def main():
    lr = LR(REDUCTIONS_FILE, LR_TABLE_FILE)
    d = "d 1 d"
    c = "c 2 c"
    input = [c, c, d, c, d]
    g_tree = lr.parse(input)
    g_tree.print()

if __name__ == '__main__':
    main()