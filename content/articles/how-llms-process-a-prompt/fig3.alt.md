Prefill, decoding et KV cache.

1. Le prompt « The capital of France is » est découpé en cinq tokens (exemple illustratif). Les cinq entrent ensemble.

2. Panneau 1, prefill : il s'exécute une seule fois. Les cinq tokens traversent chaque couche (couche 1, couche 2, … couche N) en parallèle. Chaque couche stocke une cellule K/V par token : les cellules 1 à 5 sont remplies et stockées. Phase surtout limitée par le calcul. Le délai avant le premier token (TTFT) est surtout le coût du prefill.

3. À la dernière position, les logits (un score brut par token du vocabulaire) passent par une règle de sélection (la plus simple : le meilleur score). Elle choisit le premier token de la réponse, « Paris » (exemple illustratif).

4. Panneau 2, decoding : une boucle, un token par étape. Phase souvent limitée par la mémoire, car chaque étape relit le cache. La latency entre tokens est surtout le coût d'une étape. Une étape : prendre le token choisi, en faire un vecteur, le faire passer dans toutes les couches, ajouter son K et son V au cache et faire l'attention sur tout le cache, calculer de nouveaux logits, choisir le token suivant. « Decoding » désigne ici seulement cette boucle.

5. Étape 1 : « Paris » est la seule nouvelle entrée. Chaque couche réutilise les cellules 1 à 5 sans les recalculer, ajoute la cellule 6 et fait l'attention sur 1 à 6.

6. Étape 2 : même chose, avec lecture des cellules 1 à 6 et ajout de la cellule 7.

7. Une flèche en pointillés ramène de la fin de la boucle à la nouvelle entrée. La boucle continue jusqu'à un token de fin ou une limite de longueur. Le cache gagne une cellule par couche et par étape.

Légende : cellule pleine = K/V stockés ; cellule à bord épais avec « + » = ajoutée à cette étape ; cellule en pointillés = vide, pas encore remplie.

Notes : le cache contient un K et un V par token, par couche et par KV head. Chaque couche a son cache : la couche 10 ne réutilise pas celui de la couche 3. On garde K et V, on jette Q : seule la query du dernier token sert à prédire la suite. Sans cache, chaque étape recalculerait K et V de tout l'historique.

Sources : NVIDIA, Mastering LLM Techniques: Inference Optimization (developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization) ; Hugging Face, Cache explanation (huggingface.co/docs/transformers/en/cache_explanation).
