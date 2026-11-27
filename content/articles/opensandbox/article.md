# OpenSandbox : une API pour lancer les sandboxes d'un agent

## L'essentiel

- OpenSandbox est un projet open source (Apache 2.0) qui donne aux agents une API unique pour obtenir une sandbox jetable, sur votre propre infrastructure.
- Il se place sous le harness : il ne choisit ni le modèle ni les règles de l'agent, il fournit « l'endroit où le code s'exécute ».
- Point de vue de novembre 2026 : le projet évolue vite (version 1.2.1 du 13 novembre 2026). Vérifiez son dépôt avant de décider.

## Le besoin

Un agent écrit du code ou lance des commandes que personne n'a relues. Il vaut mieux les exécuter ailleurs que sur votre machine.

![Un agent envoie du code non fiable. Sans sandbox, il s'exécute sur l'hôte. Avec une sandbox, il s'exécute dans un environnement jetable, détruit à la fin.](fig1.svg)

OpenSandbox vise ce besoin : exécuter du code, des commandes, des fichiers, un navigateur ou un bureau dans une sandbox, avec Docker en local et Kubernetes en cluster ([README](https://github.com/opensandbox-group/OpenSandbox)).

## Comment c'est organisé

Le projet sépare trois chemins : créer la sandbox, y exécuter, contrôler ce qui en sort.

![Architecture d'OpenSandbox : des SDK, la CLI osb et un serveur MCP appellent un serveur de cycle de vie. Il délègue à Docker ou à Kubernetes. Dans chaque sandbox, un daemon execd exécute les commandes. Les échanges d'exécution vont directement à la sandbox, sans repasser par le serveur.](fig2.svg)

Source(s) de la figure : [documentation d'architecture du projet](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/index.md).

Le serveur de cycle de vie crée et supprime. Les commandes, fichiers et le code passent directement par le daemon execd, avec un flux de sortie en continu. Les contrats sont des spécifications OpenAPI, avec des SDK pour cinq langages.

## La vie d'une sandbox

Une sandbox suit quatre étapes : créer, travailler, mettre en pause, détruire.

![Cycle de vie : create (à partir d'une image), run (commandes, fichiers, code), pause puis resume, delete. Une durée de vie (TTL) détruit la sandbox si personne ne la renouvelle. Un snapshot garde l'état sous forme d'image.](fig3.svg)

Source(s) de la figure : [documentation d'architecture du projet](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/index.md).

La pause et les snapshots dépendent du backend choisi. Le projet annonce aussi des pools de ressources et la création par lots pour l'évaluation et l'entraînement par renforcement.

## Réseau et secrets

Le projet contrôle le trafic dans les deux sens.

![Trafic entrant : une passerelle ingress route vers la sandbox. Trafic sortant : une politique egress, propre à chaque sandbox, filtre les domaines. Un credential vault ajoute le secret à la requête sortante : l'agent ne voit jamais le vrai secret.](fig4.svg)

Source(s) de la figure : [documentation d'architecture du projet](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/index.md) ; [README](https://github.com/opensandbox-group/OpenSandbox).

Ces contrôles sont des fonctions déclarées par le projet. Cette note ne les a pas testées. Le credential vault demande une politique egress en mode strict (dns+nft). L'isolation par défaut est celle d'un container ; les runtimes plus stricts sont une option, et la documentation réserve les modes moins restrictifs au développement local.

## Où il se place

OpenSandbox est une couche d'exécution derrière une API. Il ne remplace ni un harness, ni une politique de sécurité, ni un environnement d'évaluation.

![Trois projets, trois questions. OpenSandbox : où et comment lancer le code, par une API de sandbox. OpenShell : quelles règles encadrent l'agent, avec une politique en premier. OpenEnv : quel environnement pour entraîner ou évaluer, avec une API d'environnement (reset, step, state).](fig5.svg)

OpenSandbox et OpenShell se recoupent sur le réseau sortant et l'injection de secrets. OpenEnv est complémentaire : un environnement peut tourner dans une sandbox. Une comparaison détaillée est dans la note « Agent sandboxes : trois outils, trois questions ».

## Ce qu'il faut savoir

- Licence Apache 2.0. Le README présente OpenSandbox comme un projet de l'Agentic AI Foundation (AAIF). Les détails de gouvernance ne sont pas vérifiés ici.
- La production reste à votre charge : le serveur, la configuration de sécurité et les images.
- Le README met en garde : les versions « umbrella » actuelles ont une lacune connue de signature et de provenance. Épinglez les images par digest.
- Le README donne des temps de création (64 ms P50 pour des créations en série et 125.4 ms P99 pour 10 créations en parallèle, sandboxes Firecracker sur Kubernetes). Mesure du projet, sans test indépendant : à ne pas comparer à d'autres outils.

## Sources

- [OpenSandbox, README](https://github.com/opensandbox-group/OpenSandbox)
- [OpenSandbox, documentation d'architecture](https://github.com/opensandbox-group/OpenSandbox/blob/main/docs/architecture/index.md)
- [OpenSandbox, versions](https://github.com/opensandbox-group/OpenSandbox/releases)
- [OpenEnv, README](https://github.com/openenv/OpenEnv)
