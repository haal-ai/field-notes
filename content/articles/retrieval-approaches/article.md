# Retrieval : choisir la recherche selon la question

## L'essentiel

- Aucune méthode de retrieval ne gagne partout. Partez de la question, pas de l'outil.
- Mots exacts ou codes : keyword search. Même sens avec d'autres mots : vector search. Liens entre éléments : graph.
- Fusionner deux méthodes aide en moyenne, mais coûte sur certaines requêtes. Commencez simple et mesurez sur vos propres questions.

Cette page est un guide. Aucune expérience n'a été menée ici : elle s'appuie sur des études publiques et sur une règle pratique, pas sur une mesure.

## Partir de la question

Beaucoup d'équipes installent une base de vecteurs par réflexe. Une meilleure entrée : regarder ce que la question demande.

![Arbre de décision : mots ou codes exacts, keyword search (BM25) ; même sens avec d'autres mots, vector search ; liens entre éléments, graph ; mélange ou doute, commencer simple et ajouter une méthode à la fois (règle pratique, pas un résultat mesuré).](fig1.svg)

La règle est du bon sens d'ingénieur, pas un résultat mesuré. Elle donne un ordre de travail : commencer par la keyword search, ajouter les vecteurs si les mots diffèrent de la question, ajouter un graph si des questions de liens apparaissent.

## Trois méthodes, trois échecs typiques

Chaque méthode a un exemple où elle réussit et un où elle échoue.

![Comparaison de trois méthodes. Keyword search : trouve les mots exacts ; « erreur 221 » réussit ; « annuler mon abonnement » rate « stopper la souscription ». Vector search : compare le sens des embeddings ; « annuler mon abonnement » retrouve « stopper la souscription » ; « erreur 221 » peut ramener des erreurs voisines. Graph : suit les liens ; « quels clients ne sont pas touchés par la panne du fournisseur A ? » ; la similarité ne calcule pas un complément.](fig2.svg)

Sources de la figure : [BEIR](https://arxiv.org/abs/2104.08663) ; [DPR](https://arxiv.org/abs/2004.04906) ; [Beyond Vector Similarity](https://arxiv.org/abs/2606.06003).

Les études publiques confirment le tableau. Sur 18 jeux de données, BM25 reste une base solide, et les modèles denses déçoivent souvent hors de leur domaine ([BEIR](https://arxiv.org/abs/2104.08663)). Pour les questions-réponses ouvertes, un retriever dense entraîné a battu BM25 de 9 à 19 points sur la précision des 20 premiers passages ([DPR](https://arxiv.org/abs/2004.04906)). Une étude sur un graphe industriel minuscule (46 nœuds, 23 requêtes) montre que certaines questions de structure échappent à la similarité. C'est une preuve d'existence, pas un résultat général ([Beyond Vector Similarity](https://arxiv.org/abs/2606.06003)).

Les résultats datent de 2020 et 2021. Les encodeurs récents ont changé les écarts.

## Lire les benchmarks avec prudence

Un benchmark peut favoriser les mots exacts sans le vouloir : ses jugements de pertinence viennent souvent de systèmes à mots. Sur TREC-COVID, l'ajout de 980 jugements manquants a fait passer le modèle dense ANCE de 0,654 à 0,735 nDCG@10, soit 6,7 points au-dessus de BM25 ([BEIR](https://arxiv.org/abs/2104.08663)). Un classement dépend donc aussi de la façon dont le test a été construit.

## Fusionner deux listes : le hybrid search

Le hybrid search lance deux méthodes, puis fusionne les listes. Une fusion courante est la RRF : chaque document reçoit 1 / (60 + rang) dans chaque liste, puis on additionne ([Cormack et al.](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf)).

![Fusion RRF avec trois documents inventés. A : rang 1 et rang 1, score 0,0328. C : rang 4 et rang 2, score 0,0318. B : rang 2 et rang 5, score 0,0315. Ordre fusionné : A, C, B. Calcul avec k = 60.](fig3.svg)

Sources de la figure : [Cormack et al.](https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf) (formule, k = 60) ; [The Fusion Tax](https://arxiv.org/abs/2610.30612) (limites).

La fusion n'est pas gratuite. Dans une étude de 2026 (7 jeux BEIR, 5 encodeurs denses, 3 fonctions de fusion), même la meilleure méthode testée, une interpolation pondérée des scores et non la RRF, classe les documents pertinents sous le meilleur de ses deux composants pour 13 à 48 % des requêtes. Elle gagne pourtant en moyenne. La RRF coûte davantage quand le retriever dense est nettement plus fort ([The Fusion Tax](https://arxiv.org/abs/2610.30612)). Les auteurs conseillent de décider selon l'équilibre mesuré sur votre corpus. C'est une seule étude.

## Quand la mémoire suffit

Un index de vecteurs n'exige pas toujours une base dédiée.

![Contrôle de taille : 10 000 vecteurs × 768 nombres × 4 octets = 30 720 000 octets, soit environ 30,7 Mo. Ce volume tient en mémoire vive d'une machine ordinaire. Seuil indicatif, non mesuré ici.](fig4.svg)

À cette taille, un simple index en mémoire suffit pour stocker les vecteurs. Le seuil de 10 000 est un ordre de grandeur, pas une règle testée. La vitesse de recherche et la mise à jour comptent aussi.

## Et ensuite ?

Pour un exemple modeste de mesure plutôt que de supposition, voir le test « Petit essai de code graph » de cette bibliothèque : sur un petit projet, le graph n'a rien apporté aux questions faciles. Ce test n'a qu'un cas (n = 1).

Le sujet évolue vite : une étude RAG contre GraphRAG ([arXiv 2502.11371](https://arxiv.org/abs/2502.11371)) a été révisée en novembre 2026. Elle conclut que chaque approche a ses forces selon la tâche et que les combiner avec une stratégie de sélection aide. Vérifiez toujours les sources les plus récentes.

## Sources

- Thakur et al., BEIR : https://arxiv.org/abs/2104.08663
- Karpukhin et al., Dense Passage Retrieval : https://arxiv.org/abs/2004.04906
- Cormack, Clarke, Buettcher, Reciprocal Rank Fusion (SIGIR 2009) : https://cormack.uwaterloo.ca/cormacksigir09-rrf.pdf
- The Fusion Tax: A Diagnostic Analysis of When Hybrid Retrieval Hurts (IEEE Access, 2026) : https://arxiv.org/abs/2610.30612
- Beyond Vector Similarity: A Structural Analysis of Graph-Augmented Retrieval for Industrial Knowledge Graphs : https://arxiv.org/abs/2606.06003
- RAG vs. GraphRAG : https://arxiv.org/abs/2502.11371
