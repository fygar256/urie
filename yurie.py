#!/usr/bin/env python3
import sys

def main():
    if len(sys.argv) < 2:
        print("usage: python yurie.py program.uri")
        return

    with open(sys.argv[1], "r", newline='') as f:
        prog = f.read()

    array = [0] * 130000
    ptr = 0
    idx = 0
    length = len(prog)

    def inc_ptr():
        nonlocal ptr
        ptr += 1

    def dec_ptr():
        nonlocal ptr
        ptr -= 1

    def inc():
        array[ptr] = (array[ptr] + 1) % 256

    def dec():
        array[ptr] = (array[ptr] - 1) % 256

    def output():
        sys.stdout.write(chr(array[ptr]))
        sys.stdout.flush()

    def input_():
        ch = sys.stdin.read(1)
        array[ptr] = ord(ch) if ch else 0

    def branch_(type_):
        nonlocal idx
        idxsv = idx - 1  # '#' の位置を保存
        
        if idx < length and prog[idx] == '-':
            sign = -1
            idx += 1
        else:
            sign = 1
            
        v = 0
        while idx < length and prog[idx] in "0123456789":
            v = v * 10 + ord(prog[idx]) - 48
            idx += 1
            
        if (type_=='Z' and array[ptr] == 0) or (type_=='NZ' and array[ptr] != 0):
            idx = idxsv + sign * v

    def branchz():
        branch_('Z')

    def branchnz():
        branch_('NZ')


    ops = {
        '>': inc_ptr,
        '<': dec_ptr,
        '+': inc,
        '-': dec,
        '.': output,
        ',': input_,
        '#': branchz,
        '!': branchnz,
    }

    while idx < length:
        c = prog[idx]
        idx += 1
        op = ops.get(c)
        if op:
            op()

if __name__ == "__main__":
    main()
