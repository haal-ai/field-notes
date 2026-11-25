# A small test of code graphs: no help on easy questions, a hint on a hard one

## Conclusion first

On a small, well-named codebase, a coding agent that searched with its own tools did as well on quality as the same agent with a code graph. It answered every question correctly. On the two easy questions, the agent alone was faster than every graph run and cheaper in all but one.

On one longer question, the graph setups cost a little less. That is a lead to test. It is not a result. This page records nine runs. Nine runs cannot show that any setup is better in general.

## What a code graph is

A code graph is an index of a codebase. It lists definitions, callers, types, routes and the code a change would affect. A coding agent can query the index instead of searching files one by one.

An agent is a program that carries out the requests of a language model. It runs tools and returns their results. The set of tools and rules around the model is the harness. Here, the agent's own tools were file search, file read and shell commands.

Two public code graph tools were tested. The Entire CLI plugin entire-graph precomputes this kind of index for an agent ([entire-graph repository](https://github.com/entireio/entire-graph)). The graphify package parses code with tree-sitter, runs locally and uses no language model for code ([graphify package page](https://pypi.org/project/graphifyy/)). Both pages describe the tools as they are now. This test used the versions below.

## Test record

Test date: the artifact that holds these results was created on 13 November 2026 and revised on 17 November 2026. The exact run dates were not recorded. The runs took place between those two dates. This range is inferred from the artifact dates.

Versions: Entire CLI 0.12.2, entire-graph 0.6.0 with its no-egress setting on, and graphify 0.9.108. Graphify built its index with tree-sitter only and no model. The agent model was set to automatic selection, so the real model is not identified and may have differed between runs. The model that judged the answers is also not recorded.

Target: one private, mostly Python application with 58 files and about 6,700 lines. The index was built in a scratch copy. I do not name the application or its files.

## Method

I compared three setups. The first was the agent alone, with file search, file read and shell commands. The second was the agent with entire-graph. The third was the agent with graphify. All three used the same model setting (automatic selection, so the actual model may have differed between runs), the same prompts and a fresh context. In the two graph setups, I told the agent to prefer the graph.

I used three tasks. Two were small lookup questions. One was a long task about the effect of a change. Each setup ran each task once. That makes nine runs. The full task set had nine tasks. Only three were run.

Each task had a checklist of facts that a correct answer must contain, and a list of things it must not claim. The checklist was kept outside the repository. The source design was that a judge, not shown which setup produced the answer, scored each answer against it. The judge model is not recorded.

I measured four things. Credits are the billing unit of the platform that ran the agents. I do not convert them to money. Peak context is the most text the model held at once. Turns are the number of agent steps. Elapsed time is wall-clock seconds. The platform logged raw token counts as zero. This page reports no token numbers.

## Results

All nine answers were correct. Quality was tied, so quality does not separate the setups.

Peak context ranged from 26,411 to 44,499 across the nine runs. In the six graph-versus-alone comparisons, the graph run held more context in four and less in two. These are single runs, so I draw no conclusion from them.

On the two small tasks, neither graph setup was cheaper than the agent alone. Credits summed over both tasks were 0.800 for the agent alone, 1.255 for entire-graph and 0.947 for graphify. Per task, the agent alone used 0.288 and 0.512. Entire-graph used 0.653 and 0.602. Graphify used 0.274 and 0.673. Only one graph run cost less than the agent alone: graphify on the first task, by 0.014 credits.

The graph setups were also slower on the small tasks. On the first task the times were 25 seconds alone, 57 with entire-graph and 40 with graphify. On the second task they were 39, 50 and 61 seconds. All four graph runs were slower than the agent alone.

On the long task, credits were 1.545 alone, 1.448 with entire-graph and 1.167 with graphify. Times were 97, 111 and 98 seconds. Turns were 19, 24 and 15. Graphify used 24 percent fewer credits than the agent alone, and entire-graph used 6 percent fewer. With one run per setup, these gaps are within what chance could produce.

![Credits, elapsed seconds and turns per setup for three tasks, one run each](visual.svg)

## What the results suggest

A graph can add a step. In the source notes, the agent sometimes followed graph links and then read the file anyway. I did not examine the tool logs for this. On a small, well-named codebase, that step may cost more than it saves. This is a plausible reason. I did not test it.

The long task points the other way. Graph setups used fewer credits there. I treat this as a lead. A larger repository and more repeats are needed to confirm it.

The instruction to prefer the graph may have added cost on the small tasks. A softer instruction might narrow the gap. I did not test this either.

## Limits

This is n=1: one run per setup per task, nine runs in all. There is no repeat and no measure of spread. Only three of nine planned tasks ran. One small private repository was used. The result does not apply to large repositories, other languages or other models.

The model setting was automatic and the actual model may have differed between runs, the judge model was not recorded, and the exact run dates are inferred. Token use was not measured. Credits are specific to one platform. Newer releases of both tools may exist. Check before relying on this record, because a newer release may behave differently.

This page does not confirm or refute any vendor's savings claim. It does not rank the tools.

## Next steps

A real test needs more repositories, including a large one. It needs repeated runs per task, a gentler graph instruction, and token counts. A rerun will be a new dated result. It will not replace this record.
