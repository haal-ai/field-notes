Attention : le token « is » regarde les tokens précédents (exemple illustratif).

Cinq tokens : « The », « capital », « of », « France », « is ». Chaque token, y compris « is », porte une key K (ce qu'il propose) et une value V (le contenu à transmettre). Le dernier token, « is », produit en plus une query Q (ce qu'il cherche).

« is » compare sa query Q aux keys K des tokens précédents et à la sienne. Cette comparaison donne un attention weight par token. Les attention weights sont qualitatifs : la figure les montre par l'épaisseur des flèches et la longueur de barres, sans chiffres.

« is » mélange ensuite les values V selon ces attention weights. Le résultat est le nouveau vecteur de « is ».

Définitions : query Q = ce que je cherche ; key K = ce que je propose ; value V = le contenu à transmettre.

Encadré : une attention head est une copie indépendante de cette comparaison, avec ses propres Q, K et V. Son couple K, V s'appelle ici KV head. Un modèle exécute plusieurs têtes en parallèle. Le modèle empile des couches ; un token les traverse toutes, l'une après l'autre.

Source : Vaswani et al., Attention Is All You Need (arxiv.org/abs/1706.03762).
