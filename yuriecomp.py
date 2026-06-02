#!/usr/bin/env python3
import sys
import subprocess

HEADER = """
.section .text
.globl _start
.equ SYS_EXIT, 1
.equ SYS_WRITE, 4
.equ SYS_READ, 3
_start:
    movabs $_my_data,%rsi
"""

TAILOR = """
mov     $SYS_EXIT,%rax
xor     %rdi,%rdi
syscall
.section .bss
_my_data: .zero 130000
"""

class UrieCompiler:
    def __init__(self):
        self.ops = {
            '>': ["inc %rsi"],
            '<': ["dec %rsi"],
            '+': ["incb (%rsi)"],
            '-': ["decb (%rsi)"],
            '.': ["mov $SYS_WRITE,%rax", "mov $1,%rdi", "mov $1,%rdx", "syscall"],
            ',': ["mov $SYS_READ,%rax", "mov $0,%rdi", "mov $1,%rdx", "syscall"],
        }

    def _parse_target(self, code, i):
        """現在の位置からジャンプ先インデックスを安全にパースする"""
        n = len(code)
        start_pos = i - 1
        sign = 1
        if i < n and code[i] == '-':
            sign = -1
            i += 1
        
        num_str = ""
        while i < n and code[i].isdigit():
            num_str += code[i]
            i += 1
        
        # 数値がない場合は0とみなす
        val = int(num_str) if num_str else 0
        target = start_pos + (sign * val)
        return target, i

    def compile(self, filename, output_s):
        with open(filename, 'r') as f:
            code = f.read()

        # 1. 全ジャンプ先を収集
        jump_targets = set()
        i = 0
        while i < len(code):
            if code[i] in '#!':
                target, i = self._parse_target(code, i + 1)
                jump_targets.add(target)
            else:
                i += 1

        # 2. アセンブリ生成
        with open(output_s, 'w') as f:
            f.write(HEADER)
            i = 0
            while i < len(code):
                if i in jump_targets:
                    f.write(f"L{i}:\n")
                
                c = code[i]
                if c in self.ops:
                    f.write('\n'.join(self.ops[c]) + '\n')
                elif c in '#!':
                    target, next_i = self._parse_target(code, i + 1)
                    f.write("cmpb $0, (%rsi)\n")
                    f.write(f"{'jz' if c == '#' else 'jnz'} L{target}\n")
                    i = next_i - 1
                i += 1
            f.write(TAILOR)

def assemble(output_s):
    base = output_s.replace('.s', '')
    subprocess.run(["as", output_s, "-o", f"{base}.o"], check=True)
    subprocess.run(["ld", f"{base}.o", "-o", base], check=True)
    print(f"Build complete: {base}")

if __name__ == "__main__":
    if len(sys.argv) < 2: sys.exit(1)
    input_file = sys.argv[1]
    output_s = input_file.replace('.yuri', '.s')
    compiler = UrieCompiler()
    compiler.compile(input_file, output_s)
    assemble(output_s)
