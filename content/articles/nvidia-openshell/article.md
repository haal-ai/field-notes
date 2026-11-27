# NVIDIA OpenShell : un runtime qui gouverne ce qu'un agent peut toucher

## L'essentiel

- OpenShell est un runtime open source (Apache 2.0) qui enferme un agent dans une sandbox et applique une policy écrite à l'avance.
- Il se place autour de l'agent, pas dans le modèle : il contrôle fichiers, appels système et réseau.
- Selon NVIDIA, l'agent ne voit jamais les vrais credentials. Ce point est une affirmation du fabricant.
- Le projet est jeune (version 0.1.x, novembre 2026) : il bouge vite. Aucune sandbox ne supprime le risque de prompt injection : elle borne seulement ce que l'agent peut faire.

## Le problème

Un agent utile lit des fichiers, installe des paquets, appelle des API et utilise des secrets. Lui donner ces droits sans limite est risqué. OpenShell vise ce compromis : laisser l'agent agir, en bornant ce qu'il peut toucher.

![Sans runtime, l'agent atteint directement les fichiers, les secrets et le réseau. Avec OpenShell, chaque flux passe par une policy.](fig1.svg)

Source de la figure : [dépôt OpenShell](https://github.com/ai-openshell/openshell).

Conclusion : le problème n'est pas le modèle, c'est l'accès de l'agent à votre machine.

## Comment il fonctionne

Un gateway crée et surveille les sandboxes. Dans chaque sandbox, un superviseur fait respecter la policy autour de l'agent. Des contrôles du noyau limitent les fichiers et les appels système. Chaque connexion réseau passe par une vérification avant de sortir.

![Le CLI ou un SDK parle au gateway. Le gateway crée une sandbox. Dans la sandbox, un superviseur contrôle l'agent ; chaque connexion sortante passe par la policy.](fig2.svg)

Source de la figure : [dépôt OpenShell](https://github.com/ai-openshell/openshell).

Conclusion : l'agent ne décide pas de ses propres droits. La policy les fixe de l'extérieur.

## Les credentials, selon NVIDIA

Selon NVIDIA, l'agent ne voit jamais les vrais credentials. OpenShell les ajoute seulement aux requêtes qui partent vers un endpoint approuvé. C'est la credential injection.

![L'agent appelle une API. Le runtime ajoute le secret hors de la sandbox. L'endpoint approuvé répond. L'agent ne voit jamais le secret.](fig3.svg)

Source de la figure : [dépôt OpenShell](https://github.com/ai-openshell/openshell), affirmation de NVIDIA ; [NVIDIA](https://perspectives.nvidia.com/nvidia-openshell/limit-blast-radius-prompt-injection/).

Conclusion : si une instruction malveillante demande le secret à l'agent, il n'a rien à donner. C'est un argument du fabricant, pas un audit indépendant.

## Changer la policy, avec un humain

Quand l'agent vise une destination nouvelle, la connexion est bloquée. Selon NVIDIA, OpenShell applique alors une formal verification : elle signale l'accès risqué que le changement accorderait, par exemple un nouvel hôte avec des credentials. Ces changements attendent une relecture humaine.

![Nouvelle destination, connexion bloquée, vérification de la policy, puis un humain approuve ou refuse.](fig4.svg)

Source de la figure : [dépôt OpenShell](https://github.com/ai-openshell/openshell), affirmation de NVIDIA.

Conclusion : l'accès s'élargit pas à pas, avec une décision humaine pour les cas à risque.

## Où il se place

OpenShell est une couche de gouvernance entre le harness et le calcul. Le harness fait tourner le modèle avec ses outils. Le calcul est fourni par un driver : Docker, Podman, MicroVM ou Kubernetes. Un gateway utilise un seul driver à la fois. La liste est non exhaustive : Windows MXC et des drivers d'extension existent aussi.

![De haut en bas : modèle, harness, runtime de policy (OpenShell), calcul (Docker, Podman, MicroVM, Kubernetes).](fig5.svg)

Source de la figure : [dépôt OpenShell](https://github.com/ai-openshell/openshell).

Conclusion : OpenShell n'est ni un modèle ni un agent. Il entoure un agent existant.

## Face à OpenSandbox et OpenEnv

Ces trois projets sont proches par le nom, pas par le but.

- OpenShell : la gouvernance. Vous déclarez ce que l'agent peut toucher.
- OpenSandbox : une API générique pour exécuter du code dans des sandboxes. Elle a aussi des règles de sortie réseau, donc les deux se recoupent en partie.
- OpenEnv : une spécification d'environnements pour l'entraînement et l'évaluation par apprentissage par renforcement. Un autre usage.

La note « Agent sandboxes : trois outils, trois questions » compare les trois.

## Limites et état du projet

- Version 0.x : les API et la stabilité peuvent changer.
- Open source sous Apache 2.0. Le dépôt indique que le projet a rejoint la CNCF et que le développement a déménagé vers un nouveau dépôt.
- NVIDIA affirme que ses quatre couches (système de fichiers, réseau, processus, routage d'inférence) réduisent ce qu'une prompt injection peut provoquer.
- Limite générale, valable pour toute sandbox : elle ne rend pas une prompt injection impossible ; une règle trop large ou une action permise mais nuisible passe quand même.
- Aucun audit indépendant ni mesure de surcoût n'a été trouvé pour cette note.

Les versions et le statut changent vite. Cette page date de novembre 2026 ; vérifiez le dépôt actuel avant de décider.

## Sources

- OpenShell (README, dépôt actuel) : https://github.com/ai-openshell/openshell
- NVIDIA, 4 couches contre l'étendue d'une prompt injection : https://perspectives.nvidia.com/nvidia-openshell/limit-blast-radius-prompt-injection/
- NVIDIA, documentation OpenShell, runtimes de sandbox : https://docs.nvidia.com/openshell/latest/how-it-works/sandboxes/runtimes
- OpenSandbox (lu le 2026-11-27) : https://github.com/opensandbox-group/OpenSandbox
- OpenEnv (lu le 2026-11-27) : https://github.com/openenv/OpenEnv
