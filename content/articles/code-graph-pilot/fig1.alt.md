Essai pilote : 1 exécution par configuration et par tâche, 9 au total.

Trois configurations passent trois tâches, une fois chacune : neuf exécutions.
- Configurations : agent seul ; agent + entire-graph ; agent + graphify.
- Tâches : tâche 1 (question simple) ; tâche 2 (question simple) ; tâche longue (effet d'une modification).
- Chaque cellule du tableau : 1 exécution.

Même modèle (sélection automatique, non identifié), mêmes consignes, contexte vierge. Avec graphe : consigne de préférer le graphe.

Trois tâches sur neuf prévues ont été jouées. Les neuf réponses sont justes (9 sur 9).

Versions : Entire CLI 0.12.2 ; entire-graph 0.6.0 (sans sortie réseau) ; graphify 0.9.108 (tree-sitter seul).

Agent : programme qui lance des outils pour un modèle. Code graph : index des définitions, appelants, types, routes.
