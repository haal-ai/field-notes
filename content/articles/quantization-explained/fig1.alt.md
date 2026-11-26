Un modèle de 7 milliards de weights, weights seuls. 16 bits = 2 octets ; 7 × 10⁹ weights × 16 bits ÷ 8 bits par octet = 14 × 10⁹ octets ≈ 14 Go (1 Go = 10⁹ octets). Un bit est un chiffre binaire.

Trois barres de largeur proportionnelle, avec au-dessus une rangée de carrés (un carré = un bit par weight) :
- 16 bits par weight : 16 carrés ; 7×10⁹ × 16 ÷ 8 = 14,00 Go.
- 8 bits par weight : 8 carrés ; 7×10⁹ × 8 ÷ 8 = 7,00 Go.
- 4,25 bits par weight : 4 carrés plus une fine part pour le scale (0,25 bit) ; 7×10⁹ × 4,25 ÷ 8 = 3,72 Go (3,71875). Un trait vertical sur la barre marque les 4 bits purs : 7×10⁹ × 4 ÷ 8 = 3,50 Go.

Tableau :
- 16 bits : 7 × 10⁹ × 16 ÷ 8 = 14 Go.
- 8 bits : 7 × 10⁹ × 8 ÷ 8 = 7 Go.
- 4 bits purs : 7 × 10⁹ × 4 ÷ 8 = 3,5 Go.
- 4,25 bits (groupe de 64, un scale de 16 bits) : 7 × 10⁹ × 4,25 ÷ 8 = environ 3,7 Go.

4,25 = 4 + 16 ÷ 64 : entiers de 4 bits plus un scale de 16 bits par groupe de 64 (disposition supposée). Un modèle en cours d'exécution a besoin de plus de mémoire que ses weights ; non chiffré ici.

Deux résultats publiés : LLM.int8() : mémoire d'inférence divisée par 2 (couches feed-forward et projections d'attention) — Dettmers et al., 2022. GPTQ : 3 ou 4 bits, perte négligeable — Frantar et al., 2022. Valable pour leurs modèles et mesures.
