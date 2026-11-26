Deux voies, l'une sous l'autre.

Voie 1, weights seuls (GPTQ, AWQ) : weights en entiers de 4 bits → décoder (entier × scale) → weights décodés × activations (pour AWQ : 16 bits × 16 bits) → produit → sortie. La dequantization a lieu sur les weights, avant le produit.

Voie 2, LLM.int8() : weights int8 × activations int8 → multiplication entière → résultat entier 32 bits → dequantization (constantes de scale) → sortie 16 bits → additionner les sorties en 16 bits. La dequantization a lieu sur le résultat, après le produit.

Activations : nombres que le modèle calcule à partir de l'entrée, par opposition aux weights (fixes). Le décodage passe des weights à la sortie de chaque multiplication.

Qualité (figure : trois repères courts ; le détail suit). LLM.int8() : quelques caractéristiques (features) très grandes restent en 16 bits ; plus de 99,9 % des valeurs sont multipliées en 8 bits (Dettmers et al.). AWQ : protéger 1 % des weights saillants réduit fortement l'erreur (Lin et al.) ; valeurs mesurées hors ligne sur des entrées d'exemple pour repérer les canaux les plus importants. GPTQ : arrondis choisis par information approchée du second ordre (estime de combien l'erreur du modèle change quand chaque weight change) (Frantar et al.).

Dequantization d'un modèle entier : Transformers peut faire la dequantization, au chargement ou ensuite, vers bf16 (décimal 16 bits), par exemple pour le fine-tuning. Mémoire = celle d'un modèle sans quantization ; la précision perdue n'est pas récupérée. La taille revient, pas la précision.
