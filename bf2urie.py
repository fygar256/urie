#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brainfuck -> urie transpiler
urie 命令:
  > < + - . , #offset
  # はセルが0なら相対ジャンプ。それ以外はそのまま通過。
  Brainfuckのメモリをゼロセル(Z)とデータセル(D)が交互に並ぶ
  インターリーブ・メモリモデルとして展開して変換します。
"""

import sys

BF_OPS = set('><+-.,[]')

def parse_bf(src):
    return [c for c in src if c in BF_OPS]

def build_tokens(bf):
    # tokens: トークンのリスト。
    # 文字列の直打ち('STR', string) とジャンプ('JMP', target_index) を分ける。
    tokens = []
    stack = []  # (open_jmp_idx, open_start_idx) を保存

    for c in bf:
        if c == '+':
            tokens.append(('STR', '>+<'))
        elif c == '-':
            tokens.append(('STR', '>-<'))
        elif c == '.':
            tokens.append(('STR', '>.<'))
        elif c == ',':
            tokens.append(('STR', '>,<'))
        elif c == '>':
            tokens.append(('STR', '>>'))
        elif c == '<':
            tokens.append(('STR', '<<'))
        elif c == '[':
            open_start_idx = len(tokens)
            tokens.append(('STR', '>'))
            
            open_jmp_idx = len(tokens)
            tokens.append(['JMP', None])  # あとで飛び先(close_pad)を設定
            
            tokens.append(('STR', '<'))
            
            stack.append((open_jmp_idx, open_start_idx))
            
        elif c == ']':
            if not stack:
                raise ValueError('Unmatched ]')
            
            open_jmp_idx, open_start_idx = stack.pop()
            
            tokens.append(('STR', '>'))
            
            close_skip_idx = len(tokens)
            tokens.append(['JMP', None])  # あとで飛び先(close_pad)を設定
            
            tokens.append(('STR', '<'))
            
            tokens.append(('JMP', open_start_idx))  # [ の先頭へ戻る無条件ジャンプ
            
            close_pad_idx = len(tokens)
            tokens.append(('STR', '<'))
            
            # [ の前方ジャンプと、] のスキップジャンプの着地点を close_pad_idx に設定
            tokens[open_jmp_idx][1] = close_pad_idx
            tokens[close_skip_idx][1] = close_pad_idx

    if stack:
        raise ValueError('Unmatched [')
        
    return tokens

def transpile(bf_src):
    bf = parse_bf(bf_src)
    tokens = build_tokens(bf)
    n = len(tokens)

    # 初期サイズの推測
    sizes = [len(t[1]) if t[0] == 'STR' else 2 for t in tokens]

    # オフセットサイズが収束するまで反復計算
    for _ in range(50):
        pos = [0] * n
        acc = 0
        for i in range(n):
            pos[i] = acc
            acc += sizes[i]
            
        changed = False
        for i, t in enumerate(tokens):
            if t[0] == 'JMP':
                target_idx = t[1]
                # # の位置からの相対バイト数
                offset = pos[target_idx] - pos[i]
                # 負の数は str(offset) で '-' がつくので長さが +1 される
                new_size = 1 + len(str(offset))
                if new_size != sizes[i]:
                    sizes[i] = new_size
                    changed = True
                    
        if not changed:
            break
    else:
        raise RuntimeError('Size did not converge')

    # 最終的な位置の再計算
    pos = [0] * n
    acc = 0
    for i in range(n):
        pos[i] = acc
        acc += sizes[i]

    # ソースコードの生成
    out_parts = []
    for i, t in enumerate(tokens):
        if t[0] == 'STR':
            out_parts.append(t[1])
        else:
            target_idx = t[1]
            offset = pos[target_idx] - pos[i]
            out_parts.append(f'#{offset}')
            
    return ''.join(out_parts)

def main():
    if len(sys.argv) < 2:
        print('usage: python bf2urie.py input.bf [output.uri]')
        return
        
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        bf_src = f.read()
        
    urie = transpile(bf_src)
    
    if len(sys.argv) >= 3:
        with open(sys.argv[2], 'w', encoding='utf-8') as f:
            f.write(urie)
        print(f'Wrote {len(urie)} bytes to {sys.argv[2]}')
    else:
        print(urie)

if __name__ == '__main__':
    main()