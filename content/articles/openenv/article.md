# OpenEnv : un standard pour décrire l'environnement d'un agent

## L'essentiel

- OpenEnv est un projet open source qui décrit, avec une interface unique, l'environnement où un agent s'entraîne ou se fait évaluer.
- Il s'adresse aux personnes qui entraînent ou évaluent des agents, pas aux utilisateurs d'un assistant de code.
- Il définit le contrat entre le modèle et l'environnement. L'isolation repose sur des conteneurs Docker et des sandboxes ; OpenEnv n'est pas présenté comme un outil de sécurité, et cette page ne l'a pas évalué.
- Le projet se dit en développement précoce : ses API peuvent changer. État en novembre 2026, version v0.15.0 ([GitHub](https://github.com/openenv/OpenEnv/releases/tag/v0.15.0)).

## Le problème visé

Un agent s'entraîne souvent par RL (reinforcement learning) : il essaie, reçoit une récompense, ajuste son comportement. Il lui faut donc un grand nombre d'environnements reproductibles : jeux, terminaux, navigateurs, outils. Aujourd'hui, chacun est souvent écrit à part.

![Sans standard, chaque outil d'entraînement a besoin d'un adaptateur pour chaque environnement : N × M. Avec une interface commune, il en faut N + M (comptes symboliques, sans mesure).](fig1.svg)

Source de la figure : illustration de cette page (comptes symboliques) ; objectif général décrit dans la [documentation OpenEnv](https://openenv.github.io/OpenEnv/).

Un standard transforme un produit d'adaptateurs en une somme.

## La boucle reset, step, state

Tout environnement expose la même petite API, calquée sur Gymnasium. Le modèle, appelé policy, et l'environnement ne se parlent que par elle.

![Boucle d'un episode : reset() renvoie la première observation ; la policy choisit une action ; step(action) renvoie une observation, une reward et un indicateur « terminé » ; la boucle recommence jusqu'à la fin. state() lit l'état à tout moment.](fig2.svg)

Source de la figure : [documentation OpenEnv](https://openenv.github.io/OpenEnv/). Le billet de lancement cite `step()`, `reset()` et `close()` ; la documentation actuelle cite `reset()`, `step()` et `state()`.

Un episode va du reset à la fin de la tâche. Les rollouts joués servent ensuite à entraîner la policy.

## Un environnement, une image

Chaque environnement est empaqueté comme une image Docker. La même image tourne en local, dans une sandbox cloud ou comme Hugging Face Space. Les environnements MCP exposent en plus leurs outils sur /mcp en mode production ; l'entraînement garde step et reward.

![Une image Docker d'environnement, trois lieux d'exécution : machine locale, sandbox cloud, Hugging Face Space. Même interface dans les trois cas.](fig3.svg)

Source de la figure : [documentation OpenEnv](https://openenv.github.io/OpenEnv/).

Le projet affirme aussi que le même environnement sert à l'entraînement puis au déploiement. C'est une affirmation du projet, que cette page n'a pas testée.

## Où il se place, et face à OpenShell et OpenSandbox

OpenEnv définit la tâche et son contrat. Il se place entre les outils d'entraînement (TRL, Unsloth, SkyRL et d'autres cités par le projet) et le calcul qui exécute l'environnement.

![Trois couches : en haut, les outils d'entraînement ; au milieu, l'interface OpenEnv (reset, step, state) ; en bas, le calcul et l'isolation (conteneur, sandbox). OpenShell et OpenSandbox relèvent de cette couche du bas.](fig4.svg)

Source de la figure : [documentation OpenEnv](https://openenv.github.io/OpenEnv/) ; position de OpenShell et OpenSandbox : lecture de cette page, à confirmer par leurs propres documentations.

La différence tient en une phrase. OpenShell et OpenSandbox traitent où et sous quelles règles le code d'un agent s'exécute. OpenEnv traite ce que l'agent doit faire, ce qu'il observe et comment il est noté. Le projet dit que ses environnements peuvent tourner sur une sandbox cloud : les deux se complètent. Ils se recouvrent seulement en bordure, car OpenSandbox cite lui-même l'entraînement RL et l'évaluation parmi ses usages. La note « Agent sandboxes : trois outils, trois questions » les compare.

## Statut et limites

- Licence : BSD-3-Clause. Lancement en octobre 2025 par Meta (équipe PyTorch) et Hugging Face ([Hugging Face](https://huggingface.co/blog/openenv)), avec un comité technique ouvert à plusieurs entreprises, selon la documentation.
- Le catalogue annonce plus de 40 environnements. C'est un chiffre du projet, qui va changer.
- Les intégrations citées par le projet n'ont pas été vérifiées une à une.
- Ni preuve d'adoption large, ni gain d'entraînement mesuré ici. Ne pas lire « standard » comme « standard de l'industrie ».

## Sources

- OpenEnv, documentation : https://openenv.github.io/OpenEnv/
- OpenEnv, dépôt GitHub (licence, version v0.15.0) : https://github.com/openenv/OpenEnv
- Hugging Face, billet de lancement d'OpenEnv : https://huggingface.co/blog/openenv
- Gymnasium, API de référence : https://gymnasium.farama.org/
