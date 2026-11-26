# Glossaire

## LLM
match: LLMs?
Un LLM (large language model) est un grand modèle de langage : un programme qui a appris à prédire la suite d'un texte. Il écrit sa réponse un token à la fois.

## GPU
match: GPUs?
Le GPU est la puce graphique qui fait presque tout le calcul d'un modèle. Sa mémoire est limitée, ce qui explique la plupart des contraintes décrites ici.

## token
Un token est un petit morceau de texte : un mot, un bout de mot ou un signe. Le modèle lit et écrit des tokens, pas des lettres.

## tokenizer
Le tokenizer est le programme qui coupe un texte en tokens avant que le modèle le lise. Le découpage dépend du tokenizer choisi.

## prompt
Le prompt est le texte qu'on donne au modèle : la question, les consignes, le contexte. Le modèle écrit sa réponse à partir de lui.

## embedding
match: embeddings?
Un embedding est la liste de nombres (un vecteur) qui représente un token pour le modèle. Le modèle calcule avec ces vecteurs, jamais avec les lettres.

## attention
L'attention est le mécanisme qui laisse chaque token regarder les tokens précédents pour choisir ce qui compte. Elle produit pour chaque token une query, une key et une value.

## query, key, value
match: quer(?:y|ies)|keys?|values?
Pour chaque token, le modèle calcule trois vecteurs notés Q, K et V. La query (Q) dit ce que le token cherche ; la key (K), ce qu'il propose ; la value (V), le contenu à transmettre.

## KV head
match: KV heads?
Une KV head est le couple de key et de value (K et V) d'une attention head. Avoir moins de KV heads que de queries réduit la taille du KV cache.

## KV cache
match: KV caches?
Le KV cache garde les keys et les values (K et V) de chaque token déjà traité, pour ne pas les recalculer à chaque étape. Il grandit avec la longueur du contexte et occupe beaucoup de mémoire GPU.

## prefill
Le prefill est la première phase : le modèle lit tout le prompt d'un coup et remplit le KV cache. Il est surtout limité par le calcul.

## decoding
Le decoding est la phase où le modèle écrit la réponse, un token par étape. Chaque étape relit le KV cache, ce qui rend cette phase surtout limitée par la mémoire.

## speculative decoding
Le speculative decoding fait proposer plusieurs tokens par un petit modèle, que le grand modèle vérifie en parallèle. La distribution de sortie du grand modèle ne change pas.

## batching
match: continuous batching|batching|batch(?:es)?
Le batching consiste à traiter plusieurs requêtes ensemble pour mieux occuper le GPU. Avec le continuous batching, une requête terminée est remplacée tout de suite par une requête en attente.

## logits
Les logits sont les scores bruts que le modèle donne à chaque token possible du vocabulaire, avant le choix du suivant.

## latency
La latency est le temps d'attente. Entre deux tokens, c'est le temps d'une étape de decoding ; avant le premier token, c'est surtout le temps du prefill.

## throughput
Le throughput est la quantité de travail faite par seconde, par exemple le nombre de tokens produits par seconde pour l'ensemble des requêtes. Il ne dit rien de la latency d'une requête seule.

## memory bandwidth
La memory bandwidth est le nombre d'octets que la puce peut lire en mémoire par seconde. Quand la lecture limite la vitesse, on dit que le travail est limité par la mémoire.

## weights
match: weights?
Les weights sont les nombres appris par le modèle : ils forment l'essentiel de sa taille. Un modèle de 7 milliards de weights en compte 7 milliards.

## activations
match: activations?
Les activations sont les nombres calculés à partir de votre entrée pendant l'exécution du modèle. Contrairement aux weights, elles changent à chaque requête.

## quantization
La quantization range les weights avec moins de bits (par exemple 4 au lieu de 16) pour gagner de la mémoire. Le prix : un peu de précision.

## dequantization
La dequantization est l'opération inverse : retrouver une valeur approchée à partir de l'entier stocké, en le multipliant par le scale. Le résultat n'est jamais exactement l'original.

## scale
match: scales?
Un scale est le nombre par lequel on divise un groupe de weights avant d'arrondir, et par lequel on multiplie ensuite pour revenir. Chaque groupe a son propre scale.

## zero-point
match: zero-points?
Le zero-point est un décalage qui déplace la plage des entiers stockés. Certains formats l'ajoutent au scale pour mieux couvrir les valeurs d'un groupe.

## fine-tuning
Le fine-tuning prolonge l'entraînement d'un modèle sur des données précises pour l'adapter à une tâche.

## code graph
match: code graphs?
Un code graph est un index d'un projet de code : définitions, appelants, types et routes. Un agent peut l'interroger au lieu de lire les fichiers un par un.

## agent
match: agents?
Un agent est un programme qui lance des outils (recherche, lecture de fichiers, commandes) pour le compte d'un modèle de langage.

## FP16, FP8, bf16, int8
match: FP16|FP8|FP4|bf16|int8|int4
Formats de nombres de 16, 8 ou 4 bits. FP16, FP8 et bf16 sont des nombres à virgule ; int8 et int4 sont des entiers. Moins il y a de bits, moins il faut de mémoire.
