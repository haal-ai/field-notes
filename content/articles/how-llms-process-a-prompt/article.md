# How an LLM processes a prompt

## What to take away

- Long prompts are slow to start because prefill must process every token.
- Long answers arrive one token per step. Each step reads a larger cache, so steps can take longer in very long contexts. This is a tendency, not a measurement made here.
- Long chats cost memory because the cache grows with every token.
- Attention designs and serving engines target the cache because the cache limits decoding.

## Two jobs, not one

A large language model (LLM) answers in two phases. The first phase is prefill. The second is decoding.

Prefill reads every token of your prompt in one parallel pass. A token is a small piece of text, often a word or part of a word. Decoding then generates the answer one token at a time. Each new token depends on all the tokens before it.

Both phases use the same model. They stress the hardware in different ways. Prefill is mostly compute-bound, which means limited by raw arithmetic. Decoding is mostly memory-bound, which means limited by how fast the hardware can move data from memory. This is a general tendency, not a law. Batching many users together, or using a short context, can change the balance. [NVIDIA describes both phases](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization).

Two measures follow from the split. Time to first token (TTFT) is the wait before the first answer token appears. In a lightly loaded system, it is mostly the cost of prefill. Inter-token latency is the gap between later tokens. It is mostly the cost of one decoding step.

## Figure: the two lanes

Terms in the figure (KV cache, K, V, cell) are defined below.

![Two lanes: prefill reads the prompt once and fills the KV cache; decoding adds one token at a time and re-reads the cache.](visual.svg)

## From text to numbers

The model cannot read letters. A tokenizer first cuts your text into tokens. Each token has an integer ID. For example, the text "The capital of France is" might become five IDs. This split is illustrative, not real tokenizer output. The exact split depends on the tokenizer.

The model then turns each ID into an embedding. An embedding is a list of numbers, also called a vector, that represents the token. These vectors are what the model computes with.

## Layers

The model is a stack of layers. A layer is one repeated block of computation. Each layer takes the vectors from the layer below and returns improved vectors. Layers do not multiply tokens. One token passes through every layer in turn. The sequence length does not change inside the model.

Each layer has its own parameters. This matters later, because each layer keeps its own cache.

## Attention

Attention is the step that lets a token use information from other tokens. Each layer computes three vectors for every token: a query (Q), a key (K), and a value (V). Learned weight matrices produce them. The query says what this token is looking for. Each key says what a token offers. Each value carries the content to pass on.

The layer compares the query of the current token with the keys of the tokens before it and its own key. The comparison gives weights. The layer then mixes the values using those weights. The mix becomes the token's new vector. This is the core idea of the Transformer design in [Vaswani et al., "Attention Is All You Need"](https://arxiv.org/abs/1706.03762). Modern models run several attention heads in parallel. A head is one independent copy of this comparison, with its own Q, K, and V. This page calls one head's K and V pair a KV head.

## Prefill: read the prompt once

In prefill, all prompt tokens go through all layers together. In every layer, the model computes Q, K, and V for every prompt token. It uses Q and K to run attention. Then it keeps K and V and discards Q. In the standard design, only the newest token's query is needed to predict the next token, so old queries are not kept ([Hugging Face docs](https://huggingface.co/docs/transformers/en/cache_explanation)).

The kept K and V vectors are the KV cache. It holds one K and one V per token, per layer, per KV head. Caching is done per layer, and each layer has its own K and V, so layer 10 cannot reuse the K and V of layer 3. [NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) and the [Hugging Face docs](https://huggingface.co/docs/transformers/en/cache_explanation) both describe this.

In standard decoder-only models, the model produces logits at the last prompt position. Logits are raw scores, one for every token in the vocabulary (the full list of tokens the model knows). A selection rule picks the first answer token from them. The simplest rule takes the highest score. Other rules add randomness. This page does not cover them. The prefill keys and values are used to generate the first new token ([NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization)); the use of the last position's logits is shown in the code example of the [Hugging Face docs](https://huggingface.co/docs/transformers/en/cache_explanation).

## Decoding: write the answer one token at a time

Decoding is autoregressive. That means each new token becomes part of the input for the next step.

One decoding step has five parts:

1. Take the token chosen in the last step.
2. Turn it into an embedding.
3. Run it through every layer.
4. In each layer, compute the token's own K and V, add them to the cache, and attend over the whole cache.
5. Read the new logits and choose the next token.

The loop repeats until the model emits an end token or reaches a length limit. The word "decoding" is also used for turning token IDs back into text. This page uses decoding only for the loop above.

The cache saves work. Without it, every step would recompute K and V for the whole history. With it, each step computes them for one token only. The price is memory. Each step also reads the entire cache.

That read can become a large part of the step time, especially for long contexts. At short contexts, the model weights matter more ([NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) lists weights, keys, values and activations as memory traffic). [Shazeer, "Fast Transformer Decoding"](https://arxiv.org/abs/1911.02150) names the cost of repeatedly loading keys and values as a limit on incremental decoding.

## How big is the cache?

The cache grows with context length. NVIDIA gives the same formula ([NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization)). A rough size is:

cache bytes = 2 × layers × KV heads × head size × tokens × bytes per number

The factor 2 counts K and V. The sizes below are an illustration, not a measurement. They assume standard multi-head attention (every head has its own K and V), a 16-bit number (2 bytes), one request, and no compression.

Take 32 layers, 32 KV heads, a head size of 128, and 100,000 tokens.

- Per token: 2 × 32 × 32 × 128 × 2 bytes = 524,288 bytes, about 0.5 MB.
- For 100,000 tokens: 524,288 × 100,000 = 52,428,800,000 bytes, about 52.4 GB. Here GB means 10^9 bytes.

The cache for a single long request can be larger than a small GPU's memory. Real engines add their own overhead on top.

## Why smaller caches matter

Several designs shrink or manage the cache.

Multi-query attention (MQA) shares one K and V set across all query heads, as proposed by [Shazeer](https://arxiv.org/abs/1911.02150). Grouped-query attention (GQA) shares K and V across groups of query heads, as proposed by [Ainslie et al.](https://arxiv.org/abs/2305.13245). GQA models usually need training or uptraining to work well; it is not a drop-in switch. If 32 query heads share 8 KV heads, the cache has 8 KV heads instead of 32. In the example above, the cache falls from 52.4 GB to 13.1 GB. That is 4 times smaller, by arithmetic: 52.4 ÷ 4 = 13.1.

Serving engines also manage cache memory. The cache is large and grows during a request. [Kwon et al.](https://arxiv.org/abs/2309.06180) describe PagedAttention, which stores the cache in blocks to reduce wasted memory. The authors report 2 to 4 times higher throughput at the same latency, compared with FasterTransformer and Orca. That result applies to their own test setup only.

A different idea speeds up decoding without changing the output. In speculative decoding, a small model proposes several tokens, and the large model checks them in parallel. [Leviathan et al.](https://arxiv.org/abs/2211.17192) show this keeps the output distribution the same.

## Where this goes next

Research on very long contexts keeps changing. This page covers the stable mechanics only. Treat any newer paper as a separate claim to check against its own sources.

## Sources

- Vaswani et al., Attention Is All You Need: https://arxiv.org/abs/1706.03762
- Shazeer, Fast Transformer Decoding: https://arxiv.org/abs/1911.02150
- Ainslie et al., GQA: https://arxiv.org/abs/2305.13245
- Kwon et al., Efficient Memory Management for LLM Serving with PagedAttention: https://arxiv.org/abs/2309.06180
- Leviathan et al., Fast Inference from Transformers via Speculative Decoding: https://arxiv.org/abs/2211.17192
- NVIDIA, Mastering LLM Techniques: Inference Optimization: https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization
