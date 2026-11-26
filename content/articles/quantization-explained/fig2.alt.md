Exemple inventé : un groupe de 8 weights (pas ceux d'un vrai modèle).

1. Original, 16 bits chacun : 0,12 ; −0,80 ; 0,33 ; 0,05 ; −0,41 ; 0,64 ; −0,22 ; 0,27. Total : 8 × 16 = 128 bits.
2. Quantization : la plus grande valeur absolue est 0,80, donc scale = 0,80 ÷ 7 = 0,1143 (16 bits). Chaque weight devient arrondi(p ÷ 0,1143), un entier de 4 bits entre −8 et 7 : 1 ; −7 ; 3 ; 0 ; −4 ; 6 ; −2 ; 2. Total : 8 × 4 bits + scale de 16 bits = 48 bits.
3. Dequantization (entier × 0,1143) : 0,11 ; −0,80 ; 0,34 ; 0,00 ; −0,46 ; 0,69 ; −0,23 ; 0,23. La cellule 0,00 est entourée d'un contour épais.
4. Erreur = restitué − original, en millièmes : −6 ; ±0 ; +13 ; −50 ; −47 ; +46 ; −9 ; −41. Plus grande erreur : −0,050 (le weight 0,05 est restitué à 0,00). 0,05 ÷ 0,1143 = 0,44, arrondi à 0 → restitué à 0,00, erreur 0,05 (la plus grande du groupe). Avec perte : les valeurs restituées sont approchées.

B. Le même groupe coupé en deux groupes de 4. Hypothèses d'exemple : weights inventés ; scale = plus grande valeur absolue ÷ 7 ; entiers de −8 à 7 (entier signé de 4 bits) ; les vrais schémas diffèrent dans le détail.
- Groupe 1 : 0,12 ; −0,80 ; 0,33 ; 0,05. Plus grande valeur absolue 0,80, scale 0,1143, inchangée.
- Groupe 2 : −0,41 ; 0,64 ; −0,22 ; 0,27. Plus grande valeur absolue 0,64, scale 0,64 ÷ 7 ≈ 0,0914 ; entiers −4 ; 7 ; −2 ; 3 ; restitués ≈ −0,366 ; 0,640 ; −0,183 ; 0,274 ; 0,64 est restitué à 0,64 (à l'arrondi près).
- Erreur absolue du groupe 2, avant (groupe de 8) → après (groupe de 4) : −0,41 : 0,047 → 0,044 (mieux) ; 0,64 : 0,046 → 0,000 (mieux) ; −0,22 : 0,009 → 0,037 (empire) ; 0,27 : 0,041 → 0,004 (mieux). Erreur totale du groupe 2 : ≈ 0,143 → ≈ 0,086.

Un gros weight étire le scale et dégrade les petits. Exemple choisi à la main : seul le groupe 2 s'améliore, et pas chaque weight (−0,22 empire). Arithmétique sur nombres inventés, pas une mesure.
