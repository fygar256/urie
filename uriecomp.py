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

    def _get_code_info(self, code):
        """1パス目: ジャンプ先を特定する"""
        jump_targets = set()
        n = len(code)
        i = 0
        while i < n:
            if code[i] == '#':
                start_pos = i
                i += 1
                sign = 1
                if i < n and code[i] == '-':
                    sign = -1
                    i += 1
                num_str = ""
                while i < n and code[i].isdigit():
                    num_str += code[i]
                    i += 1
                
                val = int(num_str) if num_str else 0
                target_idx = start_pos + (sign * val)
                jump_targets.add(target_idx)
                i -= 1 # 戻す
            i += 1
        return jump_targets

    def compile(self, filename, output_s):
        with open(filename, 'r') as f:
            code = f.read()

        # ジャンプ先ラベルのセットを取得
        jump_targets = self._get_code_info(code)

        with open(output_s, 'w') as f:
            f.write(HEADER)
            
            n = len(code)
            i = 0
            while i < n:
                # 2パス目: 必要なラベルと命令のみ出力
                if i in jump_targets:
                    f.write(f"L{i}:\n")
                
                c = code[i]
                if c in self.ops:
                    f.write('\n'.join(self.ops[c]) + '\n')
                elif c == '#':
                    # #の処理（ジャンプ先計算）
                    start_pos = i
                    i += 1
                    sign = 1
                    if i < n and code[i] == '-':
                        sign = -1
                        i += 1
                    num_str = ""
                    while i < n and code[i].isdigit():
                        num_str += code[i]
                        i += 1
                    target_idx = start_pos + (sign * int(num_str if num_str else 0))
                    
                    f.write("cmpb $0, (%rsi)\n")
                    f.write(f"jz L{target_idx}\n")
                    i -= 1 
                i += 1
            
            f.write(TAILOR)

def assemble(output_s):
    base = output_s.replace('.s', '')
    print(f"Assembling {output_s}...")
    subprocess.run(["as", output_s, "-o", f"{base}.o"], check=True)
    print("Linking...")
    subprocess.run(["ld", f"{base}.o", "-o", base], check=True)
    print(f"Success: {base}")

def main():
    if len(sys.argv) < 2:
        print("usage: python uriecomp.py program.uri")
        return
    input_file = sys.argv[1]
    output_s = input_file.replace('.uri', '.s')
    compiler = UrieCompiler()
    compiler.compile(input_file, output_s)
    assemble(output_s)

if __name__ == "__main__":
    main()