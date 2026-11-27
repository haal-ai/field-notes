# Agent sandboxes : trois outils, trois questions

## L'essentiel

- NVIDIA OpenShell, OpenSandbox et OpenEnv disent tous « sandbox ». Ils répondent pourtant à trois questions différentes.
- Un seul axe les sépare : où le code de l'agent s'exécute, et qui le contrôle.
- OpenShell fixe les règles. OpenSandbox fournit l'endroit où le code tourne. OpenEnv décrit l'environnement d'entraînement ou d'évaluation.
- Les trois sont jeunes (novembre 2026). Leurs affirmations sont celles des projets, pas des mesures faites ici.

## Où chacun se place

Autour d'un agent, les trois outils n'occupent pas la même couche.

![Autour d'un agent : OpenShell entoure l'agent de règles (runtime de gouvernance) ; OpenSandbox fournit l'endroit où le code s'exécute, par une API ; OpenEnv définit la tâche, les observations et la note, côté entraînement et évaluation.](fig1.svg)

Source(s) de la figure : les trois notes dédiées de cette série ; [OpenShell](https://github.com/NVIDIA/OpenShell), [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox), [OpenEnv](https://openenv.github.io/OpenEnv/).

Conclusion : ces trois outils se complètent plus qu'ils ne se remplacent.

## Le tableau

Le tableau résume problème, couche, qui l'exploite, licence et maturité.

![Tableau comparatif : problème visé, couche, qui l'exploite, licence, maturité pour OpenShell, OpenSandbox et OpenEnv.](fig2.svg)

Source(s) de la figure : [OpenShell](https://github.com/NVIDIA/OpenShell), [OpenSandbox](https://github.com/opensandbox-group/OpenSandbox), [OpenEnv](https://github.com/openenv/OpenEnv).

Conclusion : la licence et la jeunesse se ressemblent. Le problème visé, non.

Les lignes Problème, Couche et Exploité par résument les dépôts ; c'est la lecture de cette page.

Les recoupements existent : OpenShell et OpenSandbox décrivent tous deux un contrôle du réseau sortant et une injection de secrets. OpenSandbox cite aussi l'évaluation et l'entraînement RL parmi ses usages. Ces fonctions sont déclarées par les projets ; cette page ne les a pas testées.

## Lequel regarder

Partez de votre besoin, pas du nom de l'outil.

![Guide de choix : « je veux borner ce que l'agent peut toucher » mène à OpenShell ; « je veux lancer du code d'agent dans un environnement jetable, par API » mène à OpenSandbox ; « je veux entraîner ou évaluer des agents sur des tâches reproductibles » mène à OpenEnv.](fig3.svg)

Conclusion : si votre besoin touche deux cases, combinez. Un environnement OpenEnv peut tourner dans une sandbox cloud, selon le projet.

## Limites

Aucune comparaison de performance n'est faite : chaque projet publie ses propres chiffres, sans test indépendant, et ils ne se comparent pas entre eux. Aucun outil ne donne une protection complète. Vérifiez les dépôts avant de décider.

## Pour aller plus loin

Trois notes détaillent chaque outil :

- « NVIDIA OpenShell : un runtime qui gouverne ce qu'un agent peut toucher »
- « OpenSandbox : une API pour lancer les sandboxes d'un agent »
- « OpenEnv : un standard pour décrire l'environnement d'un agent »

## Sources

- [NVIDIA OpenShell, dépôt](https://github.com/NVIDIA/OpenShell)
- [OpenSandbox, dépôt](https://github.com/opensandbox-group/OpenSandbox)
- [OpenEnv, documentation](https://openenv.github.io/OpenEnv/)
- [OpenEnv, dépôt](https://github.com/openenv/OpenEnv)
- [OpenShell, nouveau dépôt de développement](https://github.com/ai-openshell/openshell)
