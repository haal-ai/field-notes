Bits réels par weight = 4 + coût du scale (et du zero-point) réparti sur le groupe. Barres horizontales : un tronc « 4 bits » (l'axe est coupé à 4) puis une zone hachurée pour le scale, sur un axe de 4 à 6 bits.

- Groupe de 8, scale 16 bits : 4 + 16 ÷ 8 = 6 bits (8 × 4 + 16 = 48 bits ÷ 8 weights). Le scale coûte 2 bits par weight à 8 weights par groupe.
- Groupe de 32, scale 16 bits : 4 + 16 ÷ 32 = 4,5 bits.
- Groupe de 64, scale 16 bits : 4 + 16 ÷ 64 = 4,25 bits. Le scale coûte 0,25 bit par weight à 64 weights par groupe.
- Groupe de 64, scale + zero-point (2 × 16 = 32 bits par groupe) : 4 + 32 ÷ 64 = 4,5 bits.
- Groupe de 128, scale 16 bits : 4 + 16 ÷ 128 = 4,125 bits.
- Q4_K (llama.cpp) : (2 × 16 + 12 × 8 + 128 × 8) ÷ 256 = 4,5 bits. Super-bloc de 256 weights = 8 blocs de 32 ; scale et décalage de 6 bits par bloc (8 blocs × 12 bits = 96 bits = 12 × 8) ; le super-bloc ajoute deux valeurs de 16 bits (2 × 16 = 32 bits) ; 128 × 8 = 1 024 bits d'entiers (256 × 4). Total 1 152 bits ÷ 256 = 4,5.

Petits groupes : plus de scales à stocker, mais elles suivent mieux les weights. La disposition exacte varie selon l'outil : vérifier le format utilisé.
