Taille du KV cache (exemple chiffré, pas une mesure).

Formule : octets du cache = 2 (K et V) × couches × KV heads × taille de tête × tokens × octets par nombre.

Avec 32 couches, 32 KV heads, une taille de tête de 128, 100 000 tokens et 2 octets par nombre (16 bits) :
- par token : 2 × 32 × 32 × 128 × 2 = 524 288 octets, soit environ 0,5 Mo ;
- pour 100 000 tokens : 524 288 × 100 000 = 52 428 800 000 octets, soit environ 52,4 Go.

Avec 8 KV heads au lieu de 32 (partage K/V, GQA), le cache est divisé par 4 : 52,4 ÷ 4 = 13,1 Go (contrôle : 52 428 800 000 ÷ 4 = 13 107 200 000 octets).

Deux barres à l'échelle : 32 KV heads, 52,4 Go (barre pleine, 100 %) ; 8 KV heads, 13,1 Go (un quart de la longueur, 25 %) ; mention « 4 fois moins ».

Hypothèses : attention multi-têtes standard, 16 bits, une requête, sans compression ; 1 Go = 10⁹ octets. Une seule longue requête peut dépasser la mémoire d'un petit GPU, avant le surcoût des moteurs réels.

Sources : NVIDIA, Mastering LLM Techniques: Inference Optimization (developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) ; Ainslie et al., GQA (arxiv.org/abs/2305.13245).
