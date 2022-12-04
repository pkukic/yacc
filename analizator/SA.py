from constants import *
from LR import LR
import os
import sys


def get_analizator_dir():
    # get the right path to the files
    analizator_dir = os.path.abspath(os.getcwd())
    if not analizator_dir.endswith('analizator') and not analizator_dir.endswith('analizator' + os.sep):
        analizator_dir = os.path.join(analizator_dir, 'analizator')
    return analizator_dir


def main():
    analizator_dir = get_analizator_dir()

    lr = LR(os.path.join(analizator_dir, REDUCTIONS_FILE), os.path.join(analizator_dir, LR_TABLE_FILE))
    input = [line.rstrip() for line in sys.stdin.readlines()]

    g_tree = lr.parse(input)
    g_tree.print()

if __name__ == '__main__':
    main()