---
title: Brainf*ck Fake Language 'urie'
tags: Brainf*ck
author: fygar256
slide: false
---
A Thought Experiment on Turing Completeness

Since Brainfuck's structured loops are difficult to conceive of, I created a fake language 'urie' that replaces them with relative jumps.

It only has 7 instructions. It's even lower level than Brainfuck. Is "low level" an insult?

Compared to Brainfuck's 8 instructions, it has one less instruction, making it the world's fewest and lowest-level Esoteric Language.

It's similar to Brainf*ck, but the way loops and branching are done is fundamentally different. (However, as will be explained later, transpiling from Brainf\*ck is relatively easy.)

The language specification is as follows:

```
+ Increments a cell by one
- Decrements a cell by one
< Moves the pointer left
> Moves the pointer right
. Outputs one character from a cell
, Inputs one character into a cell
#100 If the cell is 0, jumps relative to the position +100
Using -100 jumps relative to the position -100.
The '-' used here has a different meaning than the '-' in command words.
100 means the 100th byte before the # command.
```

## Proof of Turing Completeness

Prove whether urie is Turing complete.

Gemini: ----------------

Here, based on a theoretical computer science approach, we will perform a constructive proof showing that "any Brainfuck program can be mechanically converted to urie (7 instructions) while completely preserving its meaning." Since Brainfuck has been proven to be Turing complete, the existence of this conversion algorithm rigorously proves that urie is also Turing complete. The biggest challenges, the "pointer shift problem" and the "always tracking zero cell problem," can be perfectly solved by introducing an interleaved memory model.

Exact Proof of Turing Completeness of urie

① Interleaved Memory Model (Zero Cell Invariant) Instead of directly deploying Brainfuck's memory on urie's memory, we alternate between "cells that are always 0 (Z)" and "cells that hold actual data (D)."

Brainfuck memory: T[0], T[1], T[2], ...

urie memory: Z[0], D[0], Z[1], D[1], Z[2], D[2], ...

[Most Important Invariant] At the start and end of each instruction's execution, the urie pointer must always be on Z[i] (zero cell). This constraint ensures that "unconditional jumps" can be reliably triggered at any given time.

② Instruction Transpilation Rules While maintaining the above invariant, the 8 Brainfuck instructions are converted one-to-one to the urie instruction sequence.

```
Explanation of BF Instruction Conversion Code to urie
+ >+< Moves the pointer to the right (D) and increments, then returns to the left (Z).

- >-< Moves the pointer to the right (D) and decrements, then returns to the left (Z).

. >.< Move the pointer to the right (D) to output, then return to the left (Z).

, >,< Move the pointer to the right (D) to input, then return to the left (Z).

> >> Move the pointer two spaces to the right (from Z[i] across D[i] to Z[i+1]).

< << Move the pointer two spaces to the left (from Z[i] across D[i-1] to Z[i-1]).

```

Up to this point, it's very simple.

Notice that after all operations are complete, the pointer always returns to Z.

③ Transforming Loops [ ] (Control Flow Resolution)

Brainfuck loops are a combination of "forward conditional jumps ([)" and "backward conditional jumps (])".

We transform this in urie as follows:

```
[ Transformation Code Snippet
> // (1) Move to D[i]. #L_fwd // (2) If D[i] == 0, jump forward to position (8) described below.
< // (3) Return to Z[i] (maintain the invariant condition for entering the loop).

Conversion code snippet for ]
> // (4) Move to D[i].
#L_skip // (5) If D[i] == 0, jump forward to position (8) described below.
< // (6) Return to Z[i]. This is only reached when D[i] != 0.
#L_back // (7) Since the pointer is Z[i] (always 0), jump 'unconditionally' backward to position (1).
< // (8) Destination (landing pad). Return to Z[i] and maintain the invariant condition.

```
(※ L_fwd, L_skip, L_back are the specific relative byte counts calculated by the transpiler.)

④ Algorithm Trace Verification: Trace whether this transformation works without failure, both when data cell D is 0 and when it is not 0.

Case A: At the start of the loop, if the data is 0 (skip the loop), the pointer is Z (value 0). > goes to D (value 0). #L_fwd is triggered, and it jumps to the last < (8) in the transformed ]. < is executed, and the pointer is Z. Result: The loop is skipped, and the pointer is Z. The invariant is maintained, and it works perfectly.

Case B: At the end of the loop, if the data is not 0 (return to the beginning of the loop), the pointer is Z (value 0). > goes to D (value not 0). #L_skip is not triggered (because the value is not 0). < is executed, and the pointer is Z (value 0). #L_back is always triggered (because its value is 0), and it jumps to the first > (1) of [. Since it lands before >, the pointer is Z. Result: It returns to the beginning of the loop, and the pointer is Z. The invariant is maintained, and it works perfectly.

⑤ Conclusion of the Proof

Using this transpilation technique, all existing Brainfuck programs can be uniquely converted into perfectly equivalent urie programs without causing data cell misalignment or zero cell corruption. Therefore, computationally, since Brainfuck is Turing complete (assuming an infinite memory tape), it is proven that the urie that has a one-to-one correspondence with it is also strictly Turing complete.

----------------End of Gemini

Usage of the programs:

```
Brainfuck to urie conversion(transpile)

％ bf2urie.py mandelbrot.bf mandelbrot.uri

Urie interpretation

% urie.py mandelbrot.uri

Urie compilation

% uriecomp.py mandelbrot.uri

the executable is for FreeBSD. it can be applied to linux with changing system call number in uriecomp.py for linux.

mandelbrot.bf can be any bf code.
