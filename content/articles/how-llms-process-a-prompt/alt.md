1. The prompt "The capital of France is" is split into five tokens: "The", "capital", "of", "France", "is" (an illustrative split).
2. Prefill runs once. All five tokens enter together and pass through every layer in parallel. Each layer stores one K/V cell per token, so cells 1 to 5 are filled in every layer. This phase is mostly compute-bound.
3. The last prompt position gives the first answer token, "Paris" (an illustrative answer).
4. Decoding runs as a loop, one token per step. This phase is often memory-bound, because each step re-reads the cache.
5. Step 1: the new token "Paris" is the only new input. Each layer reuses cells 1 to 5 (not recomputed), adds cell 6, and attends over cells 1 to 6. The model outputs the next token.
6. Step 2 does the same with the new token: it reads cells 1 to 6 and adds cell 7.
7. A dashed arrow on the right leads from the end of the loop back to the new input. The loop repeats until the model emits a stop token. The cache grows by one cell per layer per step.

Legend: filled cell = stored K/V; thick outlined cell with "+" = added this step; dashed empty cell = not yet filled.
