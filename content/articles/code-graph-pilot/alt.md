Setups: agent alone (grep, read, shell), agent with Entire graph, agent with Graphify. Same agent, same model setting (automatic selection; the actual model may have differed between runs), same prompts, fresh context. Graph setups were told to prefer the graph. Quality: all 9 answers correct, so quality does not separate the setups.

A. Two small lookup tasks (task 1, task 2), one run each. Smaller is better.

| Setup | Credits task 1 | Credits task 2 | Sum | Seconds task 1 | Seconds task 2 |
| --- | --- | --- | --- | --- | --- |
| Agent alone | 0.288 | 0.512 | 0.800 | 25 | 39 |
| Entire graph | 0.653 | 0.602 | 1.255 | 57 | 50 |
| Graphify | 0.274 | 0.673 | 0.947 | 40 | 61 |

Neither graph setup cost less than the agent alone over the two tasks. All four graph runs were slower than the agent alone on the same task.

B. One long task, one run each.

| Setup | Credits | Elapsed seconds | Turns |
| --- | --- | --- | --- |
| Agent alone | 1.545 | 97 | 19 |
| Entire graph | 1.448 | 111 | 24 |
| Graphify | 1.167 | 98 | 15 |

The source calls this gap within noise. No percentages are drawn.

## Not shown, on purpose

Tokens (logged as 0, not measured), peak context (recorded; reported in the page text, not drawn), money, percentages, any average, error bars (none exist), vendor savings claims, any claim that graphs help or do not help in general. Task numbering "task 1/task 2" replaces the source's internal task ids.
