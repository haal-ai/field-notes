Panel A, one group of 8 invented weights (not from a real model).
1. Original, 16 bits each: 0.12, −0.80, 0.33, 0.05, −0.41, 0.64, −0.22, 0.27. Total 8 × 16 = 128 bits.
2. Quantized: the largest absolute value is 0.80. Scale = 0.80 ÷ 7 = 0.1143, stored as one 16-bit value. Each weight becomes round(w ÷ 0.1143), a 4-bit integer in −8..7: 1, −7, 3, 0, −4, 6, −2, 2. Total 8 × 4 + 16 = 48 bits.
3. Dequantized (integer × 0.1143), shown to 2 decimals: 0.11, −0.80, 0.34, 0.00, −0.46, 0.69, −0.23, 0.23.
4. Error = restored − original, in thousandths (unrounded restored value): −6, ±0, +13, −50, −47, +46, −9, −41. The largest is −0.050: the weight 0.05 is restored as 0.00 (highlighted with an outline and bold label, not colour alone).

Panel B, size of a model with 7 billion weights, weights only.
| Bits per weight | Calculation | Size |
|---|---|---|
| 16 | 7×10⁹ × 16 ÷ 8 | 14.00 GB |
| 8 | 7×10⁹ × 8 ÷ 8 | 7.00 GB |
| 4.25 | 7×10⁹ × 4.25 ÷ 8 | 3.72 GB (3.71875) |

4.25 = 4 + 16 ÷ 64: 4-bit integers plus one 16-bit scale per group of 64 (assumed layout, not confirmed for any named scheme). 1 GB = 10⁹ bytes. The extra memory a running model needs is not included. In panel A, 8 weights share one scale, so the group costs 6 bits per weight, not 4.25.

## Arithmetic used
- Scale: 0.80 ÷ 7 = 0.114286, shown 0.1143 and used as 0.1143.
- Integers: 0.12→1.05→1; −0.80→−7.00→−7; 0.33→2.89→3; 0.05→0.44→0; −0.41→−3.59→−4; 0.64→5.60→6; −0.22→−1.92→−2; 0.27→2.36→2.
- Restored = integer × 0.1143: 0.1143, −0.8001, 0.3429, 0, −0.4572, 0.6858, −0.2286, 0.2286.
- Errors (restored − original): −0.0057, −0.0001 (shown ±0), +0.0129, −0.0500, −0.0472, +0.0458, −0.0086, −0.0414 (rounded to thousandths in the figure).
- Group bits: 8×16 = 128; 8×4 + 16 = 48 (6 bits per weight in this tiny group, because the scale is spread over only 8 weights). With group size 64: 64×4 + 16 = 272 bits = 4.25 bits per weight.
- Sizes: bytes = 7×10⁹ × bits ÷ 8.
