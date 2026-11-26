# Livrer avec des agents de code : vitesse, qualité, coût

## L'essentiel

- Aucune expérience n'a été menée pour cette page. C'est un résumé de recherches publiques, suivi d'une étude proposée.
- Un agent écrit du code rapidement : c'est la partie visible. Livrer, c'est aussi fusionner, vérifier en CI, exécuter et réparer.
- Plusieurs agents en parallèle peuvent chacun réussir leurs tests, puis échouer une fois combinés.
- Le parallélisme ne fait pas toujours gagner du temps. Cela dépend du découpage du travail.
- Aucune mesure publique trouvée sur le coût local contre cloud, ni sur le coût de la CI par changement d'agent.

## La chaîne de livraison

Écrire le code n'est qu'une étape. Chaque changement passe par la préparation, le code et ses tests, l'intégration, les vérifications sur le résultat combiné, puis l'acceptation. Un échec renvoie en arrière : la réparation consomme à nouveau Git, la CI, l'environnement et les agents.

![Chaîne de livraison : demande, préparation, code et tests, intégration et vérifications, acceptation, avec une boucle de réparation. Quatre ressources sont consommées à chaque tour : Git, CI, environnement, agents.](fig1.svg)

Conclusion : le coût d'une livraison inclut les tours de réparation, pas seulement la première écriture.

## Une fusion propre qui casse

Deux agents travaillent chacun sur une branche. Chaque branche passe ses propres tests. La fusion Git se fait sans conflit. Les vérifications sur le résultat combiné échouent pourtant. Exemple : l'un change la forme du résultat d'une fonction, l'autre ajoute un appelant qui attend l'ancienne forme.

![Deux branches réussissent leurs tests, la fusion est propre, mais la vérification du résultat combiné échoue ; réparation, puis nouvelle vérification.](fig2.svg)

Une étude sur 417 paires de pull requests réelles d'un même projet trouve un seul cas d'interférence sur 834 exécutions. Sur des tâches construites exprès, l'interférence atteint 97 % des exécutions. Les auteurs précisent que ce second taux ne dit rien de la fréquence réelle. Une merge queue existe pour cette raison : elle lance les vérifications requises sur le résultat combiné.

Source de la figure : [Passes Alone, Fails Together](https://arxiv.org/abs/2609.25396) ; [documentation de la merge queue GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue).

Conclusion : une fusion propre n'est pas une acceptation.

## Un agent informé contre deux agents séparés

Le benchmark ParallACT donne à un agent les deux demandes, ou une demande à chacun de deux agents qui ne se connaissent pas. Le premier réussit nettement mieux, surtout quand les demandes se contredisent. Attention : l'écart mêle deux effets, le partage d'information et le parallélisme. Prévenir les agents qu'un pair existe aide peu. Un canal de messages récupère une petite part, avec des tokens en plus.

![Taux de réussite conjointe, un setup (un harness et un modèle). Demandes contradictoires : 62 % pour un agent informé, 16 % pour deux agents parallèles. Demandes complémentaires : 86 % contre 57 %.](fig3.svg)

Source de la figure : [ParallACT](https://arxiv.org/abs/2611.00314). D'autres études donnent le même sens : en moyenne 30 % de réussite en moins pour deux agents coéquipiers que pour un agent faisant les tâches seul ([CooperBench](https://arxiv.org/abs/2601.13295)).

Conclusion : plus d'agents n'améliore rien tout seul. Un audit de neuf études trouve que 53 des 123 comparaisons appariées ne montrent plus de gain face à une baseline qui reçoit le même budget de calcul ([PACE](https://arxiv.org/abs/2611.17610), preprint récent).

## Plus rapide ? Ça dépend

Les résultats vont dans les deux sens. Ils viennent de benchmarks différents, donc on ne compare pas les barres entre elles.

![Écarts relevés par étude, sans axe commun. CodeCRDT : de 21,1 % plus rapide à 39,4 % plus lent selon la tâche, 13,1 % plus lent en moyenne. Co-Coder : jusqu'à 2,10 fois plus rapide et 35 % moins cher, face aux baselines des auteurs. Teams of Coding Agents : 3 à 7 fois le coût d'un agent seul, pour de meilleurs résultats ; c'est un coût, pas un délai.](fig4.svg)

Source de la figure : [CodeCRDT](https://arxiv.org/abs/2510.18893) (6 petites tâches TypeScript/React ; le code généré en parallèle est plus long, ce qui brouille la mesure) ; [Co-Coder](https://arxiv.org/abs/2606.00953) (28 tâches, chiffres auto-déclarés face aux baselines des auteurs) ; [Teams of Coding Agents](https://arxiv.org/abs/2610.17471) (ProgramBench : un surcoût pour de meilleurs résultats que l'agent seul, pas une mesure de vitesse).

Conclusion : le gain existe quand le découpage est bon. Sinon, l'attente et le coût montent. Un grand chantier publié par un éditeur ([exemple](https://www.anthropic.com/engineering/building-c-compiler)) montre une échelle, pas un gain : il n'a pas de comparaison avec un agent seul.

## Ce qu'il faudrait mesurer (étude proposée)

Pas d'expérience ici. Voici la méthode proposée : comparer un generalist, des specialist agents et une version hybride, avec la même exigence de qualité. Quatre compteurs restent séparés et ne s'additionnent pas : temps écoulé, argent, ressources, effort humain. Le coût se calcule par résultat accepté, donc avec les essais ratés. Les seuils (qualité, coût, délai) se fixent avant le test.

![Quatre compteurs séparés : temps écoulé (de la demande à l'acceptation), argent (modèles, CI, environnements, personnes), ressources (minutes de runner, CPU, mémoire), effort humain (mise en place, relecture, réparation). Encadré : non mesuré à ce jour.](fig5.svg)

Conclusion : trois inconnues restent ouvertes. Le coût d'un environnement local contre cloud, le coût de la CI par changement d'agent et la référence humaine n'ont pas de mesure publique que cette page puisse citer.

## Limites

Ce sont des preprints, souvent récents et parfois révisés. Les résultats valent pour les modèles et les outils testés, à la date de relecture. Les benchmarks sont petits et ne ressemblent pas toujours au travail courant. Cette page ne recommande ni outil ni modèle.

## Sources

- Passes Alone, Fails Together (sept. 2026) : https://arxiv.org/abs/2609.25396
- ParallACT (oct. 2026) : https://arxiv.org/abs/2611.00314
- CooperBench (janv. 2026) : https://arxiv.org/abs/2601.13295
- PACE (nov. 2026) : https://arxiv.org/abs/2611.17610
- CodeCRDT (oct. 2025) : https://arxiv.org/abs/2510.18893
- Co-Coder (mai 2026) : https://arxiv.org/abs/2606.00953
- Teams of Coding Agents (oct. 2026) : https://arxiv.org/abs/2610.17471
- Rapport d'ingénierie d'un éditeur (févr. 2026 ; compilateur C ; rapport d'éditeur, pas une mesure indépendante) : https://www.anthropic.com/engineering/building-c-compiler
- Documentation GitHub, merge queue : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
