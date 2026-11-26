Du texte aux nombres (exemple illustratif).

Le prompt « The capital of France is » est découpé en cinq tokens par un tokenizer : « The », « capital », « of », « France », « is ». Le découpage réel dépend du tokenizer.

Chaque token reçoit un identifiant entier, noté ici ID 1 à ID 5. Les vraies valeurs ne sont pas montrées.

L'embedding transforme chaque identifiant en vecteur : une liste de nombres, dessinée sous forme de colonne « [ … ] » sans valeurs.

Le modèle calcule avec ces vecteurs, pas avec les lettres.

La figure est lue de haut en bas : texte, tokens, identifiants, vecteurs. Deux flèches indiquent les étapes : « tokenizer » puis « embedding ».
