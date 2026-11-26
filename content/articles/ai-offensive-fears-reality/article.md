# IA offensive : les peurs et la réalité

## L'essentiel

- L'IA n'a pas inventé de nouvelle attaque. Elle abaisse la barrière d'entrée et elle accélère.
- Ce qui compte encore : l'autorisation, la vérification, les bases.

Situation au 26 novembre 2026. Le sujet change en quelques semaines. Cet article prend le point de vue du défenseur.

## Deux annonces, deux peurs

**Octobre 2026 : REA, lire et refaire un logiciel.** Selon [InfoQ](https://www.infoq.com/news/2026/10/reverse-engineer-anything/), REA (Reverse Engineer Anything) est un projet open source. Il relie des agents de code à des outils de reverse engineering existants, via des serveurs MCP. L'agent interroge un désassembleur, suit les fonctions et teste des hypothèses. Le projet ne prétend pas retrouver le code source d'origine. Ses démonstrations sont ciblées (une fonction, un calcul). Les praticiens sont partagés, et des développeurs indépendants craignent pour leurs jeux et leurs applications. Chaque utilisateur reste responsable de son autorisation. La peur : « n'importe qui peut lire et refaire un logiciel ».

**13 novembre 2026 : l'alerte FLASH du FBI.** Le FBI publie une [alerte FLASH](https://www.ic3.gov/CSA/2026/261113.pdf) sur ARTEX, un cadre open source de test d'intrusion piloté par des LLM. Selon le FBI, des acteurs malveillants variés l'utilisent depuis août 2026, dans de nombreux secteurs. L'outil transforme un objectif écrit en langage naturel en actions d'agents. Selon le FBI, citant Microsoft, certaines intrusions vont de la cible aux droits privilégiés en moins de trois heures. Le développeur a retiré le dépôt en octobre, mais l'outil circule par des copies. Plus de 1 600 consoles exposées ont été comptées début novembre. La peur : « l'IA attaque seule, vite, partout ».

![Les deux annonces, la peur qu'elles lancent et ce que disent les sources : REA (InfoQ, octobre 2026) et l'alerte FLASH du FBI (13 novembre 2026).](fig1.svg)

Source(s) de la figure : [InfoQ](https://www.infoq.com/news/2026/10/reverse-engineer-anything/) ; [FBI, FLASH-20261113-001](https://www.ic3.gov/CSA/2026/261113.pdf).

Regardons ce qui est vrai, puis ce qui reste humain. Le FBI relaie des constats d'éditeurs de sécurité : ce n'est pas une mesure indépendante.

## Ce qui est vrai

D'abord, les mêmes techniques, plus vite. Le FLASH ne cite aucune faille nouvelle. Ses cibles sont surtout des systèmes périphériques peu surveillés : portails de partenaires, applications mobiles, services anciens.

Ensuite, une capacité ancienne, un accès plus large. Le reverse engineering de logiciels compilés existe depuis des années. Des decompilers comme [Ghidra](https://github.com/NationalSecurityAgency/ghidra) ou [JADX](https://github.com/skylot/jadx) servent déjà les spécialistes, même sans agent. REA les orchestre.

![Échelle de compétence en quatre niveaux, avec leur statut : faisable maintenant (niveaux 1 et 2), possible avec des tests (niveau 3), non démontré et coûteux (niveau 4).](fig2.svg)

Source(s) de la figure : [InfoQ](https://www.infoq.com/news/2026/10/reverse-engineer-anything/) (cas ciblés) ; observations personnelles.

Avis personnel : un essai limité et en lecture seule, sur une application installée chez moi, va dans ce sens. Les niveaux 1 à 3 sont des observations personnelles, pas des mesures. Le code livré se lit mieux qu'avant. Reconstruire un produit entier reste coûteux.

Côté fonctionnement, un cadre d'agent suit une boucle de ce type, décrite par le FBI et par [GTIG](https://cloud.google.com/blog/topics/threat-intelligence/agentic-threat-activity-crosses-a-significant-threshold) :

![La boucle d'agent décrite par le FBI : objectif en langage naturel, agents, outils, résultats, retour à l'objectif. Le périmètre autorisé reste une décision humaine.](fig3.svg)

Source(s) de la figure : [FBI, FLASH-20261113-001](https://www.ic3.gov/CSA/2026/261113.pdf) ; [GTIG](https://cloud.google.com/blog/topics/threat-intelligence/agentic-threat-activity-crosses-a-significant-threshold).

Mêmes méthodes, barrière plus basse, vitesse plus haute.

## Ce qui reste humain

Une personne choisit le périmètre autorisé, vérifie qu'un résultat est réel et assume le droit d'agir. Trouver un système ne donne pas le droit de le tester. Un pentest se fait avec l'accord du propriétaire, dans un cadre convenu ([NIST SP 800-115](https://csrc.nist.gov/pubs/sp/800/115/final)).

Les résultats d'agent sont parfois faux. Selon Check Point, une campagne, observée sur une console parmi dix, n'a eu aucun gain réel malgré 400 791 messages d'agent. Dans les autres cas décrits, des accès et des données ont été obtenus.

Le FBI note deux faces. Le trafic de l'outil est très bruyant : il peut déclencher des alertes. Mais sa vitesse laisse peu de temps pour réagir. Selon GTIG, les exploits zero-day ont peu augmenté en moyenne (pic en août), alors que les divulgations et les exploits ont presque doublé entre janvier et août 2026.

![Ce qui change (vitesse, échelle, coût, barrière d'entrée, délai de correction) et ce qui reste humain (périmètre, vérification, responsabilité). Chiffres GTIG, exploits zero-day par mois : moyenne de 8 en 2025, moyenne de 11 en 2026, 22 pour le seul mois d'août 2026.](fig4.svg)

Source(s) de la figure : [GTIG](https://cloud.google.com/blog/topics/threat-intelligence/agentic-threat-activity-crosses-a-significant-threshold) ; [Check Point Research](https://research.checkpoint.com/2026/hacking-on-autopilot-inside-artex-cybercrime-campaigns/).

Ce qui ne bouge pas à la vitesse des modèles : à qui appartient la cible, et qui autorise le test. Avis personnel : les outils publics sont un plancher, pas un plafond. L'écart n'est pas mesuré.

## Que faire

Pas de défense magique : les bases, plus vite. Les recommandations du FBI servent de fil conducteur.

![Check-list défenseur en six points, reliée aux recommandations du FBI : exposition, identité et droits, secrets, limites de débit et alertes, journaux et preuves, signalement.](fig5.svg)

Source(s) de la figure : [FBI, FLASH-20261113-001](https://www.ic3.gov/CSA/2026/261113.pdf). Références générales : [CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) ; [OWASP Top 10](https://owasp.org/www-project-top-ten/) ; [NIST CSF](https://www.nist.gov/cyberframework).

Règle pratique pour qui développe : ne rien cacher dans le code livré, le supposer lisible. Le hardening reste la meilleure réponse. L'IA change le rythme, pas la liste.

## Sources

- InfoQ, Reverse Engineer Anything Project Brings AI Agents to Binary Analysis (octobre 2026) : https://www.infoq.com/news/2026/10/reverse-engineer-anything/
- FBI, Threat Overview of ARTEX Autonomous Penetration Testing Framework, FLASH-20261113-001 (13 novembre 2026, TLP:CLEAR) : https://www.ic3.gov/CSA/2026/261113.pdf
- Google Threat Intelligence Group, Agentic threat activity crosses a significant threshold (novembre 2026, rapport d'éditeur) : https://cloud.google.com/blog/topics/threat-intelligence/agentic-threat-activity-crosses-a-significant-threshold
- Check Point Research, Hacking on Autopilot: Inside ARTEX Cybercrime Campaigns (novembre 2026, rapport d'éditeur) : https://research.checkpoint.com/2026/hacking-on-autopilot-inside-artex-cybercrime-campaigns/
- Ghidra : https://github.com/NationalSecurityAgency/ghidra
- JADX : https://github.com/skylot/jadx
- CISA, Known Exploited Vulnerabilities Catalog : https://www.cisa.gov/known-exploited-vulnerabilities-catalog
- OWASP Top 10 : https://owasp.org/www-project-top-ten/
- NIST Cybersecurity Framework : https://www.nist.gov/cyberframework
- NIST SP 800-115, Technical Guide to Information Security Testing and Assessment : https://csrc.nist.gov/pubs/sp/800/115/final
