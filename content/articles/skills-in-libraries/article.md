# Des skills livrées dans les bibliothèques

## L'essentiel

- Selon les défenseurs des library skills, un agent de code apprend souvent une bibliothèque à partir d'exemples anciens et peut écrire des appels dépassés.
- Des mainteneurs placent maintenant une skill dans leur paquet. Elle voyage avec la version installée.
- pnpm trouve ces skills dans vos dépendances directes, mais ne lie rien avant votre approval.
- Le risque est la supply chain : une skill guide l'agent à chaque session et peut mentionner des scripts.

## Une skill, c'est un dossier

Une skill est un dossier avec un fichier `SKILL.md`. Il commence par un frontmatter (`name`, `description`), puis donne les instructions en Markdown. Les dossiers `scripts/`, `references/` et `assets/` sont facultatifs ([spécification Agent Skills](https://agentskills.io/specification)).

![Structure d'une skill : un dossier contenant un SKILL.md obligatoire (frontmatter name et description, puis instructions) et trois dossiers facultatifs : scripts, references, assets.](fig1.svg)

Source de la figure : [spécification Agent Skills](https://agentskills.io/specification).

À retenir : le format est simple et lisible. Une skill est du texte, pas un programme. Elle peut pourtant en référencer.

## Le chargement se fait par étapes

L'agent ne lit pas tout au démarrage. Cette progressive disclosure limite les tokens consommés.

![Chargement par étapes. Au démarrage : le nom et la description de chaque skill, environ 100 tokens (valeur indicative de la spécification). Si la tâche correspond : le SKILL.md complet, moins de 5 000 tokens recommandés. Au besoin : les fichiers de references, scripts et assets.](fig2.svg)

Sources de la figure : [spécification Agent Skills](https://agentskills.io/specification) ; [Anthropic](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

À retenir : ce sont des valeurs recommandées par la spécification, pas des mesures. Seuls le nom et la description pèsent en permanence.

## Pourquoi la mettre dans la bibliothèque

Selon les défenseurs des « library skills », un LLM a appris sur des exemples du passé. Ils veulent donc qu'une skill voyage dans le paquet publié : elle décrit alors la version installée ([Dependency Skills](https://dependencyskills.org/library-skills/)). C'est une convention proposée, pas un standard.

![Sans skill : l'agent s'appuie sur des exemples anciens et peut écrire des appels dépassés. Avec une skill livrée dans le paquet : les instructions correspondent à la version installée et changent avec elle. Exemple mesuré le 26 novembre 2026 : @trpc/server 11.31.3 contient 16 skills.](fig3.svg)

Sources de la figure : [Dependency Skills](https://dependencyskills.org/library-skills/) ; [library-skills](https://github.com/tiangolo/library-skills) ; contenu du paquet npm @trpc/server 11.31.3, mesuré le 26 novembre 2026.

À retenir : l'argument est logique, mais aucune mesure de gain de qualité n'a été trouvée. Des paquets en livrent déjà : `@trpc/server` en contient 16, et les mainteneurs de FastAPI confirment que les leurs sont voulues ([discussion](https://github.com/fastapi/fastapi/discussions/16194)).

## Du paquet à l'agent avec pnpm

Depuis la version 12.11.0, pnpm cherche des skills dans les dépendances directes de chaque projet. Il les cherche jusqu'à trois niveaux sous `skills/`. Un `pnpm install --prod` ignore celles des devDependencies ([pnpm](https://pnpm.io/agent-skills)).

![Du paquet à l'agent : 1. les mainteneurs écrivent skills/nom/SKILL.md ; 2. le paquet est publié ; 3. pnpm install la trouve dans une dépendance directe ; 4. message « Packages awaiting approval » ; 5. pnpm approve écrit l'accord dans pnpm-workspace.yaml ; 6. pnpm crée un symlink dans le dossier de skills de l'agent, vers node_modules ; 7. l'agent lit la description.](fig4.svg)

Source de la figure : [pnpm, Agent skills](https://pnpm.io/agent-skills).

À retenir : tant que vous n'approuvez pas, rien n'est lié. Une skill en attente ne fait jamais échouer l'installation. Les installations globales, `pnpm dlx` et `pnpm deploy` ne lient aucune skill. pnpm n'a pas été lancé pour cet article : ceci suit sa documentation du 26 novembre 2026.

## Pourquoi l'approval compte

La documentation de pnpm donne la raison : une skill est une instruction que l'agent suit à chaque session, et elle peut inclure des scripts qu'il lance. Un paquet de plus dans vos dépendances, c'est donc aussi du texte de plus qui guide votre agent. Le projet Dependency Skills le dit autrement : cette skill arrive chez quelqu'un qui ne l'a jamais lue.

![Ce que l'approval protège. Un paquet apporte du texte de skill et parfois des scripts ; l'agent les suit à chaque session. Avant d'approuver : lire le texte, chercher des scripts et le champ allowed-tools (expérimental), n'approuver que certaines skills avec skills: guide, migrate.](fig5.svg)

Sources de la figure : [pnpm, Agent skills](https://pnpm.io/agent-skills) ; [spécification Agent Skills](https://agentskills.io/specification).

À retenir : lisez la skill comme vous liriez un script d'installation. Approuvez les skills utiles, pas tout le paquet par réflexe.

## Et ensuite ?

Les outils bougent chaque semaine. Des outils séparés, comme `library-skills` ou `skills-npm`, font un travail voisin hors de pnpm (ils relient aussi des skills), et `skills-npm` annonce sa fusion dans la CLI skills ([skills-npm](https://github.com/antfu/skills-npm)). Cette page a donc une relecture à trois mois. Vérifiez toujours la documentation de votre outil.

## Sources

- Spécification Agent Skills : https://agentskills.io/specification
- Anthropic, Equipping agents for the real world with Agent Skills : https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- pnpm, Agent skills : https://pnpm.io/agent-skills
- Dependency Skills, library skills : https://dependencyskills.org/library-skills/
- library-skills (CLI) : https://github.com/tiangolo/library-skills
- FastAPI, discussion sur les skills dans le wheel : https://github.com/fastapi/fastapi/discussions/16194
- skills-npm : https://github.com/antfu/skills-npm
- Contenu du paquet npm @trpc/server 11.31.3, mesuré le 26 novembre 2026 (npm pack).
