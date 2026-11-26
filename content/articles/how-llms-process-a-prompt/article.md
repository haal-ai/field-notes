# Comment un LLM traite un prompt

## L'essentiel

- Un long prompt démarre lentement : le prefill lit chaque token.
- Une longue réponse arrive un token à la fois. Chaque étape relit un cache plus gros, donc elle peut ralentir en contexte très long (tendance, pas une mesure faite ici).
- Une longue conversation coûte de la mémoire : le cache grandit à chaque token.

## Du texte aux nombres

Un grand modèle de langage (LLM) autorégressif (il écrit un token à la fois) ne lit pas les lettres. Un tokenizer coupe le texte en tokens, souvent des mots ou des morceaux de mots. Chaque token devient un identifiant, puis un vecteur : un embedding.

![Le prompt « The capital of France is » découpé en cinq tokens, puis en identifiants, puis en vecteurs (exemple en anglais, illustratif ; le découpage réel dépend du tokenizer).](fig1.svg)

## L'attention : chaque token regarde les précédents

Dans chaque couche (layer) du modèle, l'attention laisse un token puiser dans les précédents. Chaque token y produit une query (Q), une key (K) et une value (V). Le résultat : un nouveau vecteur, mélange des values pondéré par la comparaison de Q aux keys ([Vaswani et al.](https://arxiv.org/abs/1706.03762)).

![Attention : le token « is » compare sa query Q aux keys K des tokens précédents et à la sienne, puis mélange leurs values V. Une KV head est le couple K et V d'une attention head (exemple illustratif).](fig2.svg)

Source de la figure : [Vaswani et al.](https://arxiv.org/abs/1706.03762).

## Deux phases, un cache

Le même modèle travaille en deux phases. Le prefill lit tout le prompt d'un coup : il est surtout limité par le calcul (compute-bound). Le decoding écrit la réponse un token à la fois : il est surtout limité par la mémoire (memory-bound). C'est une tendance, pas une loi ([NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization)).

Deux mesures en découlent. Le délai avant le premier token (time to first token, TTFT) est surtout le coût du prefill. La latency entre tokens (inter-token latency) est surtout le coût d'une étape de decoding.

Le modèle garde K et V de chaque token et jette Q ([Hugging Face](https://huggingface.co/docs/transformers/en/cache_explanation)). Ces vecteurs forment le KV cache, propre à chaque couche. Chaque étape ajoute le K et le V du nouveau token, puis relit tout le cache. Sans cache, elle recalculerait tout l'historique. La relecture pèse lourd en contexte long ([Shazeer](https://arxiv.org/abs/1911.02150)). En contexte court, les weights du modèle pèsent davantage dans la mémoire lue ([NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) cite les weights, les keys, les values et les activations).

![Prefill : cinq cellules K V remplies d'un coup. Decoding : une cellule ajoutée par couche et par étape, jusqu'au token de fin. À la dernière position, les logits (un score par token du vocabulaire) donnent le premier token de la réponse. « Paris » est un exemple illustratif.](fig3.svg)

À retenir : le cache contient un K et un V par token, par couche et par KV head. Chaque couche a son cache : la couche 10 ne réutilise pas celui de la couche 3. On garde K et V, on jette Q : seule la query du dernier token sert à prédire la suite. Sans cache, chaque étape recalculerait K et V de tout l'historique.

Sources de la figure : [NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) ; [Hugging Face](https://huggingface.co/docs/transformers/en/cache_explanation).

## Quelle taille fait le cache ?

Le cache grandit avec le contexte, selon la formule de [NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) : 2 × couches × KV heads × taille de tête × tokens × octets par nombre. Dans l'exemple, il atteint environ 52,4 Go pour 100 000 tokens : plus que la mémoire d'un petit GPU.

![Taille du cache pour 100 000 tokens (32 couches, 32 KV heads, tête de 128, 2 octets) : 524 288 octets par token, 52 428 800 000 octets au total, soit 52,4 Go. Avec 8 KV heads : 13,1 Go, 4 fois moins (exemple chiffré, pas une mesure).](fig4.svg)

Sources de la figure : [NVIDIA](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) (formule) ; [Ainslie et al.](https://arxiv.org/abs/2305.13245) (GQA).

## Trois pistes autour du cache

Trois idées s'attaquent au cache ou à son coût. Le partage de K et V, avec 8 KV heads au lieu de 32, ramène l'exemple à 13,1 Go.

![Trois pistes autour du cache. Partager K et V : MQA (un seul jeu) et GQA (un jeu par groupe) ; entraînement ou ré-entraînement en général nécessaire. Ranger par blocs : PagedAttention, throughput 2 à 4 fois supérieur à latency égale face à FasterTransformer et Orca, sur le banc d'essai des auteurs. Vérifier : le speculative decoding fait proposer des tokens par un petit modèle et les fait vérifier par le grand, sans changer la distribution de sortie.](fig5.svg)

Sources de la figure : [Shazeer](https://arxiv.org/abs/1911.02150) (MQA) ; [Ainslie et al.](https://arxiv.org/abs/2305.13245) (GQA) ; [Kwon et al.](https://arxiv.org/abs/2309.06180) (PagedAttention) ; [Leviathan et al.](https://arxiv.org/abs/2211.17192) (speculative decoding).

Ces pistes visent toutes le même goulot : le cache limite le decoding.

## Et ensuite ?

La recherche sur les contextes très longs évolue vite. Cette page ne couvre que les mécanismes stables : vérifiez tout article plus récent dans ses propres sources.

## Sources

- Vaswani et al., Attention Is All You Need : https://arxiv.org/abs/1706.03762
- Shazeer, Fast Transformer Decoding : https://arxiv.org/abs/1911.02150
- Ainslie et al., GQA : https://arxiv.org/abs/2305.13245
- Kwon et al., Efficient Memory Management for LLM Serving with PagedAttention : https://arxiv.org/abs/2309.06180
- Leviathan et al., Fast Inference from Transformers via Speculative Decoding : https://arxiv.org/abs/2211.17192
- NVIDIA, Mastering LLM Techniques: Inference Optimization : https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization
- Hugging Face, Cache explanation : https://huggingface.co/docs/transformers/en/cache_explanation
