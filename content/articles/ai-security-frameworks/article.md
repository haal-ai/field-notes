# Sécurité de l'IA : quel framework ouvrir pour quelle question ?

## L'essentiel

- Trois documents répondent à trois questions différentes. Ils ne se classent pas : on choisit selon la question.
- AISVS liste des exigences à tester dans une application. Les contrôles AICM décrivent ce qu'un service d'IA met en place. AIUC-1 produit un rapport d'audit pour un agent.
- Un même nom de contrôle ne prouve pas la même couverture. Vérifiez le périmètre avant de réutiliser une preuve.
- Les chiffres datent du 2026-11-26. Ces standards évoluent vite.

## Trois questions, trois vues

Un framework est un cadre de référence : une liste d'exigences ou de contrôles. Pour la sécurité de l'IA, trois documents publics se complètent.

![Trois vues de la sécurité de l'IA. AISVS : quelles exigences tester dans cette application ? AICM et STAR for AI : quels contrôles ce service a-t-il, et qui les fournit ? AIUC-1 : quelles preuves externes pour cet agent ? Chaque vue produit une preuve différente. Ce n'est pas un classement.](fig1.svg)

Source(s) de la figure : [OWASP AISVS](https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/) ; [CSA AICM v1.1](https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1) ; [AIUC-1, périmètre](https://standard.aiuc-1.com/scoping).

AISVS est volontairement étroit. Il ne couvre que ce qui est propre à l'IA. Ce n'est ni une méthode de gestion des risques, ni un certificat. Utiliser sa liste ne délivre aucun certificat.

## Du contrôle à l'évaluation du fournisseur

Un fournisseur de service d'IA peut répondre aux contrôles AICM par un questionnaire, l'AI-CAIQ. Ce questionnaire alimente le programme STAR for AI.

![De la liste de contrôles à l'évaluation. L'AICM liste 247 objectifs de contrôle dans 18 domaines. L'AI-CAIQ pose les questions au fournisseur. STAR for AI niveau 1 : auto-évaluation publiée dans un registre public. Niveau 2 : évaluation indépendante (certification ISO ou attestation SOC 2, avec l'AICM), après le niveau 1.](fig2.svg)

Source(s) de la figure : [CSA AICM v1.1](https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1) ; [CSA, STAR for AI](https://cloudsecurityalliance.org/blog/2026/11/17/csa-star-for-ai-certifications-what-are-they).

Le niveau 1 reste une déclaration du fournisseur. Le niveau 2 suppose une inscription au niveau 1. Seul lui fait intervenir un tiers indépendant.

## Un audit pensé pour les agents

AIUC-1 vise les agents d'IA uniquement. Il compte 50 exigences, réparties en 6 principes. L'auditeur signe un Statement of Applicability : la liste de ce qui est vraiment audité. Le rapport indique le périmètre et la version du standard.

![De l'audit au rapport. Définir le périmètre de l'agent. Établir le Statement of Applicability : contrôles de base par défaut, exclusion d'une exigence justifiée par écrit et validée par l'auditeur, contrôles complémentaires au choix. Rassembler les preuves et lancer les tests techniques. Obtenir le rapport d'audit et le certificat. Selon son propriétaire, l'ensemble prend en général 4 à 8 semaines, avec des tests refaits chaque trimestre et un nouvel audit chaque année.](fig3.svg)

Source(s) de la figure : [AIUC-1, périmètre](https://standard.aiuc-1.com/scoping) ; [AIUC-1, certification](https://standard.aiuc-1.com/aiuc-1-certification).

Attention : le processus et ses délais sont la description du propriétaire du standard, pas une mesure indépendante. Le propriétaire précise lui-même qu'un certificat ne garantit pas la sécurité et que la certification vise des produits précis. Aucun numéro de version d'AIUC-1 n'était visible le 2026-11-26, et le standard est mis à jour chaque trimestre.

## Une preuve, plusieurs exigences ?

Un même enregistrement de test peut parfois servir à plusieurs frameworks. Il contient la configuration, le résultat attendu, le résultat obtenu et les journaux.

![Réutiliser une preuve. Un enregistrement de test (configuration, résultat attendu, résultat obtenu, journaux) est relié à une exigence de chaque framework. Condition : mêmes conditions de test, même périmètre, même version. Sinon, refaire le test. Exemple générique, sans chiffres.](fig4.svg)

Source de la figure : conseil de l'auteur, sans source externe. Les sources précisent seulement que des correspondances entre frameworks existent.

Un nom de contrôle identique ne prouve pas une couverture identique. Comparez le périmètre, la version, les réglages, les exclusions et la méthode de test. C'est un conseil, pas un fait sourcé.

## Et au-dessus ?

D'autres documents se situent à un autre niveau : le NIST AI RMF (version 1.0 en 2023, révision annoncée), la norme ISO/IEC 42001 (système de management, 2023) et la loi européenne sur l'IA, l'EU AI Act. Ils définissent la gestion des risques, un système de management et des obligations légales, pas des cas de test. AISVS se présente comme leur niveau d'implémentation. Cette page ne donne ni détail ni date pour l'EU AI Act.

## Quel document pour quelle décision ?

- Plan de tests techniques : AISVS.
- Revue d'un fournisseur : AICM et AI-CAIQ.
- Assurance externe d'un agent : rapport AIUC-1.

C'est une façon de choisir, pas une règle. Les trois documents ne sont pas classés, et leur recouvrement n'est pas mesuré.

## Sources

- OWASP AISVS : https://owasp.github.io/www-project-artificial-intelligence-security-verification-standard-aisvs-docs/
- CSA, AI Controls Matrix v1.1 : https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1
- CSA, STAR for AI : https://cloudsecurityalliance.org/blog/2026/11/17/csa-star-for-ai-certifications-what-are-they
- AIUC-1, périmètre : https://standard.aiuc-1.com/scoping
- AIUC-1, certification : https://standard.aiuc-1.com/aiuc-1-certification
- NIST, AI Risk Management Framework : https://www.nist.gov/itl/ai-risk-management-framework
- ISO/IEC 42001 : https://www.iso.org/standard/42001
