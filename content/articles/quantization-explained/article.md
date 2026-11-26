# Quantization : faire tenir un modèle dans moins de mémoire

La quantization range chaque weight du modèle avec moins de bits. Le fichier et la mémoire des weights diminuent. Le prix : un peu de précision, parfois un peu de qualité. Un modèle « 4 bits » coûte en réalité un peu plus de 4 bits par weight. Cette page traite du stockage des weights, pas de la vitesse.

## Un modèle est un énorme tableau de nombres

Un modèle de langage est surtout un tableau de **weights**. Un modèle de 7 milliards de weights en compte 7 milliards. À 16 bits chacun, il pèse 14 Go. La **quantization** réduit cette taille.

![Un modèle de 7 milliards de weights : 14 Go à 16 bits, 7 Go à 8 bits, 3,5 Go à 4 bits](fig1.svg)

Deux articles publics montrent que cela marche dans leurs tests. LLM.int8() divise par deux la mémoire d'**inférence** (inference : exécuter un modèle entraîné) des couches feed-forward (les couches de calcul du réseau) et des projections d'attention, sans perte de performance ([Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)). GPTQ passe à 3 ou 4 bits avec une perte négligeable ([Frantar et al., 2022](https://arxiv.org/abs/2210.17323)). Ces résultats valent pour leurs modèles et leurs mesures, pas pour tous les modèles.

## Quantization d'un groupe : scale et arrondi

On découpe les weights en **groupes** (groups). Chaque groupe partage un **scale**. On divise chaque weight par le scale, on arrondit à l'entier, on stocke l'entier. Pour réutiliser le weight, on multiplie l'entier par le scale : c'est la **dequantization**. Le résultat approche l'original : la quantization est « avec perte » (lossy). Les formats de llama.cpp utilisent aussi cette disposition par blocs, avec un scale par bloc ([ggml-common.h](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)).

![Un groupe de 8 weights inventés : scale 0,1143, entiers de 4 bits, valeurs restituées, erreurs, puis le même groupe coupé en deux](fig2.svg)

Les petits weights souffrent le plus : 0,05 est arrondi à 0 et restitué à 0,00. À retenir : un gros weight étire le scale et dégrade les petits weights du groupe. Des groupes plus petits suivent mieux les tailles locales, mais pas toujours weight par weight. Les nombres sont inventés : c'est de l'arithmétique, pas une mesure sur un vrai modèle.

## Dequantization : décoder à la volée

La plupart des méthodes qui font la quantization des seuls weights (weight-only quantization) décodent les entiers juste avant la multiplication matricielle (le calcul central du modèle : il combine le tableau de weights avec les **activations**, les nombres calculés à partir de votre entrée ; voir plus bas). AWQ note que le matériel ne multiplie pas directement un entier de 4 bits par un décimal de 16 bits ([Lin et al., 2023](https://arxiv.org/abs/2306.00978)). Formule : valeur restituée = entier × scale. Certains formats ajoutent un **zero-point** (un décalage qui déplace la plage des entiers), vu dans la figure ([ggml-quants.c](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-quants.c)).

![Dequantization à la volée : entiers de 4 bits en mémoire, décodage dans le noyau, puis multiplication ; formules avec zero-point](fig3.svg)

Les weights restent petits en mémoire. GPTQ décrit un noyau (kernel, petit programme du GPU) qui fait la dequantization « dynamiquement » et « au besoin » (traduction ; [Frantar et al., 2022](https://arxiv.org/abs/2210.17323)). AWQ fusionne le décodage dans le noyau de multiplication, sans écrire les weights décodés en mémoire principale ; le décodage donne des nombres de 16 bits (FP16) ([Lin et al., 2023](https://arxiv.org/abs/2306.00978)).

Exemple Q4_0 (llama.cpp) : les entiers sont stockés + 8, donc entre 0 et 15. Le décodeur retranche 8 à chaque valeur de 4 bits, puis multiplie par le scale du bloc, bloc par bloc sur une ligne. Premier weight : 1 + 8 = 9 ; (9 − 8) × 0,1143 = 0,1143, le même résultat. Le décalage change le stockage, pas le sens. Pour Q4_1, la valeur stockée est multipliée par le scale, puis on ajoute un minimum stocké. Pour le zéro de l'exemple : 0 × 0,1143 = 0,00, pas 0,05. L'arrondi a perdu l'écart, et le décodage ne le rend pas.

Attention : cet exemple vient d'une routine de référence qui convertit une ligne en décimaux (flottants de 32 bits). Cette page ne dit pas que la multiplication matricielle de llama.cpp passe par elle. Le scale est stocké en 16 bits : il est donc arrondi lui aussi.

Décoder ajoute du calcul, mais la génération de texte est souvent limitée par la memory bandwidth (octets lus par seconde par la puce, le GPU). GPTQ le dit : les produits matrice-vecteur (multiplications avec une seule colonne d'entrée) sont « principalement limités par la memory bandwidth » ; la dequantization « consomme du calcul en plus », mais le noyau « accède à beaucoup moins de mémoire » (traduction). AWQ avance le même argument pour la génération de tokens. Cette page ne le mesure pas. Le gain dépend du matériel et du batch size (nombre de requêtes traitées ensemble) ; pour de grands batches, GPTQ note que ses noyaux ne s'appliquent pas directement.

### L'autre voie : multiplier les entiers

Certaines méthodes appliquent aussi la quantization aux **activations** (les nombres calculés à partir de votre entrée, par opposition aux weights, fixes). Le matériel multiplie alors des entiers, et la dequantization porte sur le résultat. C'est la voie de LLM.int8() ([Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)).

![Deux voies : décoder les weights avant le produit, ou multiplier des entiers puis faire la dequantization du résultat (LLM.int8())](fig4.svg)

Transformers (Hugging Face) peut aussi faire la dequantization d'un modèle entier, au chargement ou ensuite, par exemple vers bf16, pour le fine-tuning. La mémoire redevient celle d'un modèle sans quantization, et la précision perdue ne revient pas ([Hugging Face Transformers, « Dequantize a model »](https://huggingface.co/docs/transformers/main/en/quantization/dequantize)).

## « 4 bits » coûte plus de 4 bits

Chaque groupe stocke aussi son scale, parfois un zero-point. Le coût réel par weight dépasse donc 4 bits, d'autant plus que les groupes sont petits : c'est un compromis. La disposition exacte varie selon l'outil : vérifiez la vôtre. Un modèle en cours d'exécution a besoin de plus de mémoire que ses weights ; cette page ne chiffre pas ce surplus.

![Coût réel par weight : 4 bits plus le scale, selon la taille du groupe, le zero-point et le format Q4_K](fig5.svg)

Détail du format Q4_K et du calcul de la taille du modèle : voir la figure ([ggml-common.h](https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h)).

## Ce que la quantization coûte en qualité

L'arrondi ajoute de l'erreur, inégalement. LLM.int8() garde en 16 bits quelques caractéristiques (features) très grandes ; plus de 99,9 % des valeurs restent en 8 bits ([Dettmers et al., 2022](https://arxiv.org/abs/2208.07339)). AWQ indique que protéger 1 % des weights saillants réduit fortement l'erreur ([Lin et al., 2023](https://arxiv.org/abs/2306.00978)). Résultats des tests de ces articles.

L'arrondi simple traite tous les weights pareil. GPTQ choisit ses arrondis avec une information approchée du second ordre : il estime de combien l'erreur change quand un weight change ([Frantar et al., 2022](https://arxiv.org/abs/2210.17323)). AWQ mesure hors ligne les valeurs sur des entrées d'exemple pour repérer les canaux (channels) importants ([Lin et al., 2023](https://arxiv.org/abs/2306.00978)).

## Comment juger un modèle avec quantization

Ne vous fiez pas au nombre de bits. Lancez votre tâche sur le modèle d'origine et sur le modèle avec quantization, avec des réponses connues. Comparez la qualité, pas seulement la taille. Notez le modèle, le format, la taille de groupe et la date.

## Limites

Exemples sur nombres inventés, pas des mesures. Aucun outil testé, vitesse non mesurée. Aucun format décrit au-delà de Q4_K, Q4_0 et Q4_1.

## Sources

Toutes consultées le 2026-11-25. Résumé d'AWQ lu dans sa version arXiv actuelle (v6, mise à jour le 2026-04-25) ; article de 2023.

- Dettmers et al., « LLM.int8() », 2022 : https://arxiv.org/abs/2208.07339
- Frantar et al., « GPTQ », 2022 : https://arxiv.org/abs/2210.17323
- Lin et al., « AWQ », 2023 : https://arxiv.org/abs/2306.00978
- llama.cpp, `ggml/src/ggml-common.h` (dont `block_q4_K`) : https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-common.h
- llama.cpp, `ggml/src/ggml-quants.c` (`dequantize_row_q4_0`, `dequantize_row_q4_1`) : https://github.com/ggml-org/llama.cpp/blob/master/ggml/src/ggml-quants.c
- Hugging Face Transformers, « Dequantize a model » : https://huggingface.co/docs/transformers/main/en/quantization/dequantize
