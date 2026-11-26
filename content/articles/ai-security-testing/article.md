# Tester la sécurité d'un agent : des vérifications bornées

## L'essentiel

- Tester un agent commence par une frontière : ce qu'il peut vraiment faire, pas ce qu'il dit.
- Chaque exigence se vérifie par deux essais appariés, un autorisé et un refusé, jugés par un observer extérieur au modèle.
- Un « non » du modèle ne prouve pas que le système bloque. Étiquetez chaque résultat selon ce que vous avez réellement observé.
- Les sept étapes, les rôles, les deux essais et les six étiquettes forment une méthode de travail proposée sur cette page, pas un standard.
- Cette page est défensive. Elle ne donne ni exploit, ni payload, ni cible.

## De la frontière à la décision

On part des capacités réelles de l'agent, puis on avance par petites étapes. Les personnes gardent deux décisions : le périmètre et le déploiement.

![De la frontière à la décision en sept étapes : frontière, zone de test, inventaire, cas avec oracle, exécution, classement des preuves, conservation et nettoyage. Une personne décide du périmètre et du déploiement.](fig1.svg)

Source de la figure : méthode de travail proposée sur cette page (pas un standard). Pour le contexte des exigences vérifiables, voir [OWASP AISVS](https://github.com/OWASP/AISVS).

Un testing agent prépare. Des personnes tranchent.

## Qui fait quoi

Quatre rôles restent séparés : le testing agent, le driver, le produit testé et l'observer. Le driver est le script qui envoie les requêtes. L'observer enregistre l'effet réel, hors de ce que le modèle affirme. Une personne relit et juge.

![Quatre rôles, plus une personne qui juge : le testing agent prépare, le driver envoie, le produit agit, l'observer enregistre l'effet, une personne juge. L'observer ne croit pas la réponse du modèle.](fig2.svg)

Source de la figure : méthode de travail proposée sur cette page.

Ici, « observation indépendante » veut dire séparée de ce que dit le modèle testé. Ce n'est pas une évaluation externe.

## Deux essais appariés

Chaque exigence reçoit un cas autorisé et un cas refusé. Avant le test, on fixe l'oracle : l'observation qui juge le résultat, par exemple un compteur ou un journal de requêtes.

![Cas A : la décision est « refuser », le compteur attendu est 0. Cas B : la décision est « autoriser », le compteur attendu est 1. Le cas B sert de contrôle positif : il prouve que le montage fonctionne (exemple illustratif, compteur fictif).](fig3.svg)

Source de la figure : méthode de travail proposée sur cette page. Les valeurs 0 et 1 sont un exemple illustratif.

Le refus seul ne suffit pas. Il ne compte que si le chemin autorisé, lui, aboutit. Sinon, la fixture (le jeu de données fictif) est peut-être cassée.

## Six étiquettes pour les résultats

Un « non » du modèle avant tout appel d'outil montre un comportement. Il ne montre pas un blocage. Seul un guardrail appliqué par le système, observé par l'observer, prouve l'enforcement.

![Six étiquettes, de la preuve la plus forte à la plus faible : enforcement observé ; comportement du modèle observé ; source seulement ; bloqué par compatibilité ; erreur de fixture ou incertain ; sans objet. Chacune indique ce qu'elle montre et ce qu'elle ne montre pas.](fig4.svg)

Source de la figure : vocabulaire de travail proposé sur cette page (pas un standard).

Un succès ou un échec isolé prouve peu. Notez les répétitions, les variantes et les changements de modèle. [NIST AI 100-2 E2025](https://csrc.nist.gov/pubs/ai/100/2/e2025/final) fournit un vocabulaire commun pour les attaques et les mesures de protection.

## Quatre points de vue sur les mêmes preuves

Trois cadres publics et une base de vulnérabilités éclairent les mêmes observations. Ils ne se remplacent pas.

![Quatre points de vue autour d'une même boîte « observation et limites » : AISVS (exigences techniques vérifiables, 3 niveaux, version 1.01), AICM version 1 (243 objectifs de contrôle, 18 domaines, questionnaire AI-CAIQ), AIUC-1 (standard de certification pour agents : périmètre, évaluations, audit, certification), OSV (failles connues des paquets).](fig5.svg)

Sources de la figure : [OWASP AISVS](https://github.com/OWASP/AISVS) ; [CSA AI Controls Matrix](https://cloudsecurityalliance.org/artifacts/ai-controls-matrix) (version 1 ; la page signale une version 1.1 plus récente, non citée ici) ; [AIUC-1](https://www.aiuc-1.com/) (description du propriétaire du standard, pas une mesure indépendante) ; [OSV](https://google.github.io/osv.dev/).

Une même observation peut nourrir plusieurs cadres. Chaque exigence se relit pourtant à part : une correspondance ne prouve pas une couverture. Cette façon de faire est une méthode de travail proposée, pas une méthodologie officielle combinée.

Côté OSV, une alerte connue ne prouve pas que la faille est exploitable. Un résultat vide ne couvre ni les failles inconnues ni un inventaire incomplet. Décidez aussi quelles métadonnées de paquets peuvent quitter l'organisation.

## Et ensuite ?

Les cadres évoluent vite : AISVS prépare la 1.02, AIUC-1 se met à jour régulièrement. Vérifiez l'édition citée avant d'appliquer quoi que ce soit.

## Sources

- OWASP, AI Security Verification Standard (AISVS), version 1.01 : https://github.com/OWASP/AISVS
- Cloud Security Alliance, AI Controls Matrix (version 1) : https://cloudsecurityalliance.org/artifacts/ai-controls-matrix
- AIUC-1, site du standard : https://www.aiuc-1.com/
- OSV, introduction : https://google.github.io/osv.dev/ ; API : https://google.github.io/osv.dev/api/
- NIST, AI 100-2 E2025, Adversarial Machine Learning (mars 2025) : https://csrc.nist.gov/pubs/ai/100/2/e2025/final
