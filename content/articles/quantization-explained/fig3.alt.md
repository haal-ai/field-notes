Dequantization à la volée, en trois étapes reliées par des flèches.

1. Mémoire principale (GPU) : les weights sont des entiers de 4 bits plus un scale de 16 bits par groupe. Une flèche « lecture : peu d'octets » mène au noyau.
2. Noyau de multiplication (kernel ; un noyau est un petit programme exécuté sur le GPU) : a. décoder : entier × scale (pour AWQ : nombre de 16 bits, FP16) ; b. multiplier par les activations d'entrée.
3. Résultat : produit matriciel.
Une flèche en pointillés barrée, du noyau vers la mémoire, indique que, pour AWQ, les weights décodés ne sont pas réécrits en mémoire principale.

Formule 1 : valeur restituée = entier stocké × scale. Exemple : −7 × 0,1143 = −0,8001 → −0,80 ; 0 × 0,1143 = 0,00 (pas 0,05 : l'arrondi a perdu l'écart ; le décodage ne le rend pas).
Formule 2 (zero-point) : valeur restituée = (entier stocké − zero-point) × scale.
Q4_1 : valeur stockée × scale + minimum stocké.

Exemple Q4_0 (llama.cpp) : le décodeur retranche 8 à chaque valeur de 4 bits, puis multiplie par le scale du bloc, bloc par bloc sur une ligne. Les entiers sont stockés + 8, donc entre 0 et 15. Premier weight : 1 + 8 = 9 ; (9 − 8) × 0,1143 = 0,1143 : même résultat. Le décalage change le stockage, pas le sens.
Avertissement : routine de référence qui convertit une ligne en décimaux ; cette page ne dit pas que la multiplication matricielle de llama.cpp passe par elle.

Types de sortie : AWQ → FP16 (décimal de 16 bits) ; décodeur de référence llama.cpp → flottants de 32 bits ; le scale est stockée en 16 bits, donc arrondie elle aussi.

Définitions. Multiplication matricielle : calcul central d'un modèle ; elle combine le tableau de weights avec les nombres qui le traversent. Produit matrice-vecteur : multiplication avec une seule colonne d'entrée. Noyau : petit programme exécuté sur le GPU.

Pourquoi gagner du temps : moins d'octets à lire (limite = memory bandwidth : octets par seconde que la puce lit en mémoire). Coût : du calcul de décodage en plus. Non mesuré ici. GPTQ : les produits matrice-vecteur sont « principalement limités par la memory bandwidth » ; la dequantization « consomme du calcul en plus », mais le noyau « accède à beaucoup moins de mémoire ». AWQ : même argument pour la génération de tokens. Limite : gain dépendant du matériel et du batch size (nombre de requêtes traitées ensemble) ; GPTQ : pour de grands lots, le calcul peut redevenir limitant et ses noyaux ne s'appliquent pas directement.
