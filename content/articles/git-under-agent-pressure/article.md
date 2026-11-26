# Git sous la pression des agents

## L'essentiel

- Un push fait deux choses : il ajoute des objets (qui ne changent jamais), puis il déplace une branche (un pointeur partagé). Seul le second geste doit être ordonné.
- Les agents poussent beaucoup plus souvent que les humains. L'ordre des écritures devient le goulot.
- Chaque fournisseur place cet ordre ailleurs. Ensuite, la CI et la fusion deviennent la limite suivante.
- Tous les chiffres de performance ci-dessous viennent des fournisseurs eux-mêmes. Aucun n'est une mesure indépendante.

## Un agent n'utilise pas Git comme une personne

Une personne clone une fois, travaille des heures, puis fait un push de temps en temps. Un agent dans le cloud démarre avec un espace vide, clone à chaque tâche et fait un commit après presque chaque action. Des milliers d'agents poussent vers leurs propres branches, et chaque push lance la CI.

![Une personne et un agent face à Git : rythme du clone, des commits et des push, avec les chiffres rapportés par GitHub et GitLab (données des fournisseurs).](fig1.svg)

Source(s) de la figure : [GitHub](https://github.blog/engineering/architecture-optimization/building-git-infrastructure-for-agent-scale-development/) ; [GitLab](https://about.gitlab.com/blog/scaling-git-for-the-agentic-software-factory/) ; [Entire](https://entire.com/blog/a-git-forge-without-a-center).

GitHub dit que ses pushes ont été multipliés par 4,9 en un an. C'est un chiffre rapporté par GitHub.

## Un push, deux gestes

Un push envoie d'abord des objets : commits, arbres, fichiers. Chaque objet est nommé par l'empreinte de son contenu (content-addressed). Il ne change donc jamais, et plusieurs machines peuvent le stocker en parallèle sans se mettre d'accord ([Git book](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects)). Ensuite, le push déplace une branche : un pointeur partagé. Ce second geste doit être ordonné.

![Un push en deux temps : des objets immuables stockés en parallèle, puis une branche (ref) déplacée une écriture à la fois.](fig2.svg)

Source(s) de la figure : [Git book](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects) ; [GitHub](https://github.blog/engineering/architecture-optimization/building-git-infrastructure-for-agent-scale-development/) ; [Entire](https://entire.com/blog/a-git-forge-without-a-center).

Tout le reste de la page tient dans cette idée : où place-t-on l'ordre ?

## Le verrou de GitHub, en novembre 2026

GitHub garde par défaut cinq replicas de chaque repository. Une écriture exige un quorum, mais attend tous les replicas en bonne santé, dans la limite d'un délai. Elle tient aussi un lock sur tout le repository. Le replica le plus lent fixe donc la durée de l'écriture. Selon GitHub, la moitié du trafic Git passe désormais par Azure, à environ 25 ms d'aller-retour, avec plusieurs allers-retours par écriture ([GitHub](https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/)).

![Deux agents poussent vers deux branches différentes. Avec un lock par repository, le second attend. Avec un lock par branche, ils avancent ensemble. Exemple pédagogique, pas un chiffre de GitHub.](fig3.svg)

Source(s) de la figure : [GitHub](https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/).

GitHub passe à un lock par ref. Il annonce, pour des écritures vers des refs différentes, un débit 3 à 4 fois supérieur dans ses tests internes (chiffre du fournisseur, montage non publié).

La cible est une nouvelle architecture, appelée Rubicon. Les objets vivent dans Azure Blob Storage. Les refs et la liste des packs vivent dans un service de log répliqué, Ref-CAS. Chaque mise à jour de ref y est un compare-and-swap validé par un quorum. Une transaction ne verrouille que les refs qu'elle touche. En novembre 2026, cette architecture est en aperçu privé limité ; GitHub annonce un déploiement plus large pour début 2027. GitHub cite 5 000 agents et 7 200 pushes par seconde sur un repository : c'est un test interne de GitHub, pas une mesure indépendante ([GitHub](https://github.blog/engineering/architecture-optimization/inside-githubs-new-git-storage-architecture/)).

## Cinq réponses à la même question

Chaque fournisseur déplace l'ordre à un endroit différent, avec un coût différent.

![Cinq réponses : GitHub, GitLab, Anthropic Scion, Cursor Origin et Entire. Pour chacune : où vont les objets, où la branche est déplacée, ce qui est sacrifié. État en novembre 2026.](fig4.svg)

Source(s) de la figure : [GitHub](https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/) ; [GitHub, nouvelle architecture](https://github.blog/engineering/architecture-optimization/inside-githubs-new-git-storage-architecture/) ; [GitLab](https://about.gitlab.com/blog/scaling-git-for-the-agentic-software-factory/) ; [Anthropic](https://www.anthropic.com/research/redesigning-source-control) ; [Cursor](https://cursor.com/blog/git-at-any-scale) ; [Entire](https://entire.com/blog/a-git-forge-without-a-center).

Quatre d'entre elles (GitHub, Anthropic, Cursor, Entire) reposent sur un compare-and-swap : la branche ne bouge que si elle a la valeur attendue. En novembre 2026, Anthropic décrit Scion comme un système interne qu'elle ne propose pas à d'autres. GitLab décrit sa version comme une bêta privée.

## La limite suivante : la CI et la fusion

Aller plus vite sur le stockage déplace le problème en aval, écrit GitLab. Une merge queue teste chaque changement avec ceux qui le précèdent. Si l'un échoue, ceux qui suivent repartent ([GitHub docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) ; [GitLab docs](https://docs.gitlab.com/ci/pipelines/merge_trains/)).

![Trois façons d'entrer dans une branche : sans file, deux changements valides seuls cassent ensemble ; avec une merge queue, chacun est testé avec les précédents ; chez Anthropic, on fusionne puis on teste avant le déploiement.](fig5.svg)

Source(s) de la figure : [GitHub docs](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue) ; [GitLab docs](https://docs.gitlab.com/ci/pipelines/merge_trains/) ; [Anthropic](https://www.anthropic.com/research/redesigning-source-control).

Anthropic dit qu'elle n'a pas réussi à reproduire une file avec lock global à son échelle. Elle teste donc après la fusion, et accepte que des changements concurrents entrent en conflit. Elle rapporte passer d'environ 2 500 à plus de 30 000 fusions par jour entre mai et septembre 2026 (chiffre du fournisseur).

## À retenir

Un agent pousse vite et souvent. Les objets passent à l'échelle facilement ; le déplacement de la branche, non. Chaque design choisit un endroit pour l'ordre, puis la CI devient le goulot. Les produits décrits ici changent vite : cette page est un instantané de novembre 2026.

## Sources

- GitHub, Building Git infrastructure for agent-scale development : https://github.blog/engineering/architecture-optimization/building-git-infrastructure-for-agent-scale-development/
- GitHub, Inside GitHub's new Git storage architecture : https://github.blog/engineering/architecture-optimization/inside-githubs-new-git-storage-architecture/
- GitHub, The bridge to agent-scale Git infrastructure : https://github.blog/engineering/architecture-optimization/the-bridge-to-agent-scale-git-infrastructure/
- GitLab, Scaling Git for the agentic software factory : https://about.gitlab.com/blog/scaling-git-for-the-agentic-software-factory/
- GitLab docs, merge trains : https://docs.gitlab.com/ci/pipelines/merge_trains/
- GitHub docs, managing a merge queue : https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/managing-a-merge-queue
- Anthropic, Redesigning source control at Anthropic : https://www.anthropic.com/research/redesigning-source-control
- Cursor, Git at any scale : https://cursor.com/blog/git-at-any-scale
- Entire, A Git Forge Without a Center : https://entire.com/blog/a-git-forge-without-a-center
- Git book, Git objects : https://git-scm.com/book/en/v2/Git-Internals-Git-Objects

