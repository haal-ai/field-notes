# Petit essai de code graph : aucun gain sur les questions simples, une piste sur une question difficile

## En bref

Sur une petite base de code bien nommée, un agent seul répond aussi bien qu'avec un code graph : les neuf réponses sont justes. Sur les deux questions simples, il est plus rapide que toutes les exécutions avec graphe, et moins cher sauf une fois. Sur une question longue, le graphe coûte un peu moins de crédits. C'est une piste, pas un résultat : neuf exécutions ne prouvent rien en général.

## Le dispositif

Trois configurations, trois tâches, une exécution chacune.

![Trois configurations (agent seul, entire-graph, graphify) croisées avec trois tâches : neuf exécutions](fig1.svg)

Un agent est un programme qui lance des outils pour un modèle de langage. Un code graph est un index des définitions, appelants, types et routes d'une base de code.

## Ce que fait un graphe

L'agent interroge l'index au lieu de lire fichier par fichier.

![Deux chemins vers la réponse : chercher fichier par fichier, ou interroger l'index du graphe](fig2.svg)

## Résultats

La qualité ne départage rien. Les crédits sont l'unité de facturation de la plateforme ; je ne les convertis pas en argent.

### Deux petites tâches

Le graphe ne fait gagner ni crédits ni secondes.

![Crédits et secondes par configuration pour les tâches 1 et 2 : l'agent seul est le plus rapide et le moins cher, sauf graphify sur la tâche 1 pour les crédits](fig3.svg)

### Une tâche longue

Graphify : 24 % de crédits en moins que l'agent seul ; entire-graph : 6 %. Avec une seule exécution, ces écarts restent dans le bruit.

![Tâche longue : crédits, secondes, tours et contexte maximal pour l'agent seul, entire-graph et graphify](fig4.svg)

## Fiche de l'essai

| Élément | Valeur |
| --- | --- |
| Dates | Résultats créés le 13 nov. 2026, révisés le 17 nov. 2026. Dates d'exécution non notées, entre les deux (déduction) |
| Versions | Entire CLI 0.12.2, entire-graph 0.6.0 (sans sortie réseau), graphify 0.9.108 (tree-sitter seul) |
| Modèle | Sélection automatique, non identifié, peut avoir varié |
| Cible | Application privée (index construit dans une copie temporaire ; application et fichiers non nommés), surtout Python, 58 fichiers, environ 6 700 lignes |
| Consigne | Avec graphe : préférer le graphe |
| Notation | Liste de faits cachée, juge censé ignorer la configuration (modèle juge non noté) |
| Mesures | Crédits, contexte maximal (plus grande quantité de texte tenue par le modèle à un instant donné), tours, secondes. Tokens enregistrés à zéro : non rapportés |

## Lecture prudente

Un graphe peut ajouter une étape : l'agent suivait parfois ses liens, puis lisait le fichier quand même. Je n'ai pas examiné les journaux. La consigne de préférer le graphe a peut-être alourdi les petites tâches. Ces deux explications sont plausibles, non testées.

## Limites

![Limites de l'essai : une exécution par cas, trois tâches sur neuf, un seul petit dépôt privé](fig5.svg)

Une exécution par cas, sans dispersion. Trois tâches sur neuf prévues. Un seul petit dépôt : rien ne vaut pour les grands dépôts, d'autres langages ou d'autres modèles. Des versions plus récentes des outils existent peut-être. Cette page ne confirme ni ne réfute les économies annoncées par un éditeur et ne classe pas les outils.

Une vraie suite demande plusieurs dépôts dont un grand, des répétitions, une consigne plus souple et des tokens. Elle sera un nouveau résultat daté.

## Sources

Les deux pages décrivent les outils tels qu'ils sont aujourd'hui ; l'essai a utilisé les versions de la fiche.

- [Dépôt entire-graph](https://github.com/entireio/entire-graph) : précalcule l'index pour l'agent.
- [Page du paquet graphify](https://pypi.org/project/graphifyy/) : analyse avec tree-sitter, en local, sans modèle de langage pour le code.
