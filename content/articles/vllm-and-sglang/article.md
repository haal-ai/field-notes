# vLLM and SGLang: two ways to stop wasting GPU memory

Checked on 2026-11-25 against vLLM v0.34.0 and SGLang v0.5.23, the latest releases on their GitHub release pages that day. Next review due in three months.

## The short answer

vLLM and SGLang are open-source servers that run large language models. Both save GPU memory by managing one thing well: the KV cache. I describe vLLM as built around memory packing and scheduling, and SGLang as built around reusing shared prompt text. That is my simplification. Each project now does some of both, so the best choice depends on your own workload.

SGLang is not SLANG, the shader language from NVIDIA and Khronos. The two are unrelated.

## What an inference server does

An inference server sits between your application and the model. It accepts HTTP requests and turns text into tokens. It runs the model on a GPU and streams tokens back. Both projects do this: see the [vLLM](https://github.com/vllm-project/vllm) and [SGLang](https://github.com/sgl-project/sglang) repositories.

A token is a small piece of text, often part of a word. The model reads the whole prompt first. This step is called prefill. It then writes the answer one token at a time. This step is called decode.

## One request, five steps

![One request in vLLM and SGLang, five steps, with the one step where they differ](visual.svg)

## The expensive resource is the KV cache

While the model reads text, it stores intermediate results for every token. This store is the KV cache (key-value cache). It lets the model avoid re-reading the whole text for each new token. The cache grows with every request, so it fills GPU memory fast.

The authors of the vLLM paper profiled older serving systems. They found that only 20.4% to 38.2% of KV cache memory held real token data. The rest was lost to reserved-but-unused space and to fragmentation (gaps between blocks of memory). See the introduction and Figure 2 of the [paper (PDF)](https://arxiv.org/pdf/2309.06180) by Kwon et al., 2023. That is the authors' own measurement on the systems they tested.

## How vLLM saves memory

vLLM splits the cache into small fixed-size blocks. This idea is called PagedAttention. It works like paging in an operating system. Blocks need not sit next to each other in memory, so little space is lost ([paper](https://arxiv.org/abs/2309.06180)).

Block size changed recently. Older descriptions say 16 tokens per block. In vLLM v0.34.0 the default is 64. You can pass `--block-size 16` to keep the old value ([v0.34.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.34.0)). Treat any fixed number you see elsewhere with care.

A batch is the group of requests the GPU processes together. vLLM uses iteration-level scheduling, often called continuous batching. After each step, finished requests leave and waiting requests join. The GPU does not wait for the slowest request. The paper describes this behavior and credits the earlier Orca system for it ([paper](https://arxiv.org/abs/2309.06180)).

For repeated text, vLLM uses prefix caching. It computes a hash for each full block. A hash is a short fingerprint of data. Here it is made from the block's own tokens and the hash of the block before it. A new request with the same start can reuse blocks with matching hashes. Only full blocks are cached. The default hash function is sha256 since v0.11. A request can also carry an optional cache salt. The salt keeps different users' caches apart ([vLLM design page](https://docs.vllm.ai/en/stable/design/prefix_caching/)).

## How SGLang saves memory

SGLang bets that many requests start with the same text, such as a system prompt or a shared document. Its RadixAttention keeps the KV cache of shared prefixes in a radix tree. A radix tree is a tree where requests with the same start share the same branch. A new request finds its longest matching prefix and computes only the rest ([SGLang paper](https://arxiv.org/abs/2312.07104); [LMSYS post](https://www.lmsys.org/blog/2024-01-17-sglang/)).

SGLang batches requests in the same way. Its scheduler source code keeps a running decoding batch and labels it "for continuous batching" ([scheduler.py](https://raw.githubusercontent.com/sgl-project/sglang/main/python/sglang/srt/managers/scheduler.py), a code comment, read on 2026-11-25).

The paper's authors report up to 6.4 times higher throughput than the baselines they tested. Throughput here means tokens produced per second. This is the authors' claim on their own tasks, against the baselines available when the paper first appeared in December 2023. It does not describe current versions.

SGLang also has HiCache. It adds slower, larger tiers under GPU memory: host memory first, then external storage.

The SGLang team reports up to 15.5 times higher effective input throughput in one test ([SGLang blog](https://www.sglang.io/blog/hicache)). The test used the DeepSeek-V4-Flash model on four H200 GPUs. It ran multi-turn conversations, where each new request repeats the earlier turns. The storage tier was Mooncake, an external store for KV cache. The baseline was GPU memory only: 9.4K against 145.5K tokens per second. Effective input throughput counts all input tokens served per second, including tokens whose KV cache was reused instead of recomputed. So it is not raw compute speed. It is one setup chosen by the project, and the cache hit rate was near 98%.

An earlier post reports up to 6 times throughput and up to 80% lower time to first token ([LMSYS](https://lmsys.org/blog/2025-09-10-sglang-hicache/)). Time to first token (TTFT) is the wait before the first answer token appears. Both are the project's own best cases.

## The projects have converged

The split above is a teaching aid, not a fact about today's code. vLLM now has prefix caching, as described above. Its v0.34.0 notes also list an opt-in cache-aware admission ordering, enabled with the flag `--cache-aware-admission-window` ([v0.34.0 release notes](https://github.com/vllm-project/vllm/releases/tag/v0.34.0)). SGLang's v0.5.23 notes say that DeepSeek-style MLA models running decode context parallelism can keep their prefix cache in HiCache file-based L3 storage (the slowest tier) ([v0.5.23 release notes](https://github.com/sgl-project/sglang/releases/tag/v0.5.23)). Expect both to keep changing.

## What the benchmarks say

Independent head-to-head tests are rare, and they age fast. One recent example is a benchmark by Winder.ai, an AI consultancy that runs both servers in its own systems and sells consulting, not either server. It ran the tests on one NVIDIA H100 80GB GPU, rented on 2026-09-25, with vLLM 0.30.0 and SGLang 0.5.20. Those versions are a few releases behind vLLM v0.34.0 and SGLang v0.5.23, so the numbers may differ from today's releases. The gap is exact: vLLM is four releases behind, SGLang three ([Winder.ai](https://winder.ai/vllm-vs-ollama-vs-sglang-llm-inference-comparison/)).

The load was the same for both servers: requests of about 900 prompt tokens and 256 output tokens, 20 warm-up requests, then 200 measured requests, at 1, 10 and 50 requests in flight. The metric was output tokens per second. The harness and pinned versions are published in the [winderai/llm-inference-benchmark](https://github.com/winderai/llm-inference-benchmark) repository.

On Llama 3.1 8B (FP16 weights: the model's numbers stored as 16-bit values), the two servers were close. At 1, 10 and 50 requests in flight, vLLM produced 150, 1,235 and 3,688 tokens per second. SGLang produced 154, 1,233 and 3,617. Winder.ai reports that two full runs agreed within 1% to 4% on throughput.

On Qwen3.8-27B (8-bit FP8 weights: the model's numbers stored as smaller 8-bit values, which uses less memory and is usually faster), SGLang produced 1,725 tokens per second at 50 requests and vLLM produced 1,610. Each server first needed one setting changed. The model mixes two kinds of attention layers, and each running request needs extra memory to hold its own running state, on top of the usual KV cache. SGLang capped itself at 20 running requests with default settings and served 982 tokens per second at 50; its figure above is a second run with that memory enlarged. vLLM refused to start until its sequence limit was lowered.

A second test disagrees on which server is faster. ZenML ran it on 2026-10-09 with vLLM 0.31.0 and SGLang 0.5.20 on one H100 and Qwen3.8-27B ([ZenML](https://www.zenml.io/benchmarks/sglang-vs-vllm)). It replayed recorded coding-agent traffic: 124 sessions, 32 at a time, one run per setting. ZenML reports that SGLang with default settings reached 0.53 times vLLM's tokens per second. Its best SGLang setting, with the radix cache off, reached 0.84 times. ZenML did not measure run-to-run variation and did not publish its traffic recordings. The two tests used different traffic and settings, and each used one run per setting or few runs, so neither settles the question. Both say not to read the result as a ranking. Test your own workload.

The test has limits. The prompts shared only a short start, so it did not measure prefix caching. It did not measure answer quality or more than one GPU. I did not rerun it. Read it as one setup on one machine, not as a ranking.

## How to choose

Test your own workload. Measure how much of your prompt text is shared, how many requests run at once, which model you use, and on which hardware. Treat any published speed ratio, including those above, as one result from one setup.

## Related status note

Hugging Face's Text Generation Inference (TGI) is in maintenance mode, "as of 12/11/2025" in the page's own date format ([Inference Endpoints documentation](https://huggingface.co/docs/inference-endpoints/engines/tgi)). That page recommends vLLM or SGLang as alternatives. If you compare servers, check each project's current status.

## Context

SGLang came out of LMSYS. LMSYS announced an SGLang Consortium on 2026-11-12 ([announcement](https://lmsys.org/blog/2026-11-12-sglang-consortium)).

## What I did not check

I did not run these servers. I did not read the vLLM or SGLang source code, apart from the one scheduler comment cited above. All speed figures come from the cited sources. Defaults, flags and features change between releases. Check the release notes for your version.
