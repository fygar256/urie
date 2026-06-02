#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brainfuck -> yurie transpiler
yurie 命令:
  > < + - . , #offset  !offset
  # はセルが0なら相対ジャンプ、! はセルが0でなければ相対ジャンプ
  オフセットは '#' / '!' の位置からの相対バイト数
"""

import sys

BF_OPS = set('><+-.,[]')

def parse_bf(src):
    return [c for c in src if c in BF_OPS]

def build_tokens(bf):
    tokens = []  # list of ('op',c) or ('jz',close_idx) or ('jnz',open_idx)
    stack = []
    for c in bf:
        if c in '><+-.,':
            tokens.append(('op', c))
        elif c == '[':
            idx = len(tokens)
            tokens.append(('jz', None))  # placeholder
            stack.append(idx)
        elif c == ']':
            if not stack:
                raise ValueError('Unmatched ]')
            open_idx = stack.pop()
            close_idx = len(tokens)
            tokens.append(('jnz', open_idx))
            # link open -> close
            tokens[open_idx] = ('jz', close_idx)
    if stack:
        raise ValueError('Unmatched [')
    return tokens

def transpile(bf_src):
    bf = parse_bf(bf_src)
    tokens = build_tokens(bf)
    n = len(tokens)

    # initial sizes
    size = [1 if t[0]=='op' else 2 for t in tokens]  # minimal '#0'

    # iterative fixpoint for offset-dependent sizes
    for _ in range(50):  # enough
        pos = [0]*n
        acc = 0
        for i in range(n):
            pos[i] = acc
            acc += size[i]
        changed = False
        for i, t in enumerate(tokens):
            if t[0] == 'op':
                new_size = 1
            elif t[0] == 'jz':
                close_idx = t[1]
                target_pos = pos[close_idx] + size[close_idx]  # after matching ]
                offset = target_pos - pos[i]
                new_size = 1 + (1 if offset < 0 else 0) + len(str(abs(offset)))
            else:  # jnz
                open_idx = t[1]
                target_pos = pos[open_idx] + size[open_idx]  # after matching [
                offset = target_pos - pos[i]
                new_size = 1 + (1 if offset < 0 else 0) + len(str(abs(offset)))
            if new_size != size[i]:
                size[i] = new_size
                changed = True
        if not changed:
            break
    else:
        raise RuntimeError('Size did not converge')

    # final emit
    # recompute pos once more
    pos = [0]*n
    acc = 0
    for i in range(n):
        pos[i] = acc
        acc += size[i]

    out_parts = []
    for i, t in enumerate(tokens):
        if t[0] == 'op':
            out_parts.append(t[1])
        elif t[0] == 'jz':
            close_idx = t[1]
            target_pos = pos[close_idx] + size[close_idx]
            offset = target_pos - pos[i]
            out_parts.append(f'#{offset}')
        else:  # jnz
            open_idx = t[1]
            target_pos = pos[open_idx] + size[open_idx]
            offset = target_pos - pos[i]
            out_parts.append(f'!{offset}')
    return ''.join(out_parts)

def main():
    if len(sys.argv) < 2:
        print('usage: python bf2yurie.py input.bf [output.yuri]')
        return
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        bf_src = f.read()
    yurie = transpile(bf_src)
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(yurie)
        print(f'Wrote {len(yurie)} bytes to {sys.argv[2]}')
    else:
        print(yurie)

if __name__ == '__main__':
    main()
