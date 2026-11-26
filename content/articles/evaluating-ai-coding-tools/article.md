# Comment évaluer un outil de code IA

## L'essentiel

- Un score public ne suffit pas : ses tests peuvent être faux, et nos impressions de vitesse peuvent se tromper.
- Un test local honnête part du même code et de la même consigne pour chaque outil, avec une grille cachée.
- On juge le diff de l'agent, avec deux juges de familles différentes et une règle de départage écrite.
- On note toujours le coût à côté de la qualité.

## Pourquoi un score public ne suffit pas

Un benchmark public sert de point de départ, pas de verdict. Il peut se tromper, ou avoir été vu à l'entraînement.

![Trois raisons de se méfier d'un score public. Tests : dans un audit de 27,6 % de SWE-bench Verified, sous-ensemble de problèmes que les modèles ratent souvent, au moins 59,4 % des problèmes examinés avaient des tests qui rejettent des solutions correctes. Contamination : les modèles de pointe testés ont montré des signes d'exposition aux problèmes. Perception : dans l'étude METR de début 2025, leurs tâches duraient 19 % de plus avec l'IA et ils croyaient aller 20 % plus vite. Les audits viennent d'OpenAI, qui utilise ces benchmarks : pas une source indépendante. Le 59,4 % ne vaut pas pour tout Verified.](fig1.svg)

Sources de la figure : [OpenAI, SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/) ; [OpenAI, SWE-Bench Pro](https://openai.com/index/separating-signal-from-noise-coding-evaluations/) ; [METR, étude 2025](https://arxiv.org/abs/2507.09089) ; [METR, mise à jour 2026](https://metr.org/blog/2026-02-24-uplift-update/).

Ces audits sont menés par OpenAI, qui utilise ces benchmarks : ce sont des auto-déclarations documentées, pas des contre-expertises. Plus récemment, OpenAI a cessé de publier SWE-bench Verified, puis a retiré sa recommandation de SWE-Bench Pro. METR dit aujourd'hui que sa nouvelle série de mesures est peu fiable à cause d'effets de sélection. Le chiffre de 2025 est donc daté. Retenez la méthode, pas le chiffre.

## Un test local, pas à pas

Un test local répond à votre question, sur votre code. Chaque outil reçoit le même point de départ.

![Sept étapes d'un test équitable : même code réel et même consigne ; grille cachée aux outils ; une exécution par outil ; collecte du diff, des journaux de tests, du coût et des plantages ; notation en aveugle ; réconciliation des notes ; rapport. Méthode générique, sans mesure.](fig2.svg)

Dans ce schéma, séparez l'outil du modèle : changez un seul des deux à la fois. Sinon, vous ne saurez pas lequel explique l'écart. Quand des tests existent, utilisez-les : ils vérifient la correction, sans avis.

## Juger le changement, pas toute l'application

Le diff isole le travail de l'agent. Le reste du code était déjà là.

![Barre de 100 % du code. Environ 5 % (exemple illustratif) sont le diff de l'agent. Un juge qui lit tout dilue le signal. Un juge qui lit seulement le diff isole le travail, mais voit moins bien comment il s'insère dans l'ensemble.](fig3.svg)

Les deux choix ont un prix : le diff isole, mais il perd le contexte. Dites lequel vous prenez.

## Deux juges et une règle de départage

Un LLM judge note vite, mais il a des biais. Il favorise la première réponse, la plus longue, ou celle qui ressemble à ce qu'il écrirait ([Zheng et al.](https://arxiv.org/abs/2306.05685) ; [Wataoka et al.](https://arxiv.org/abs/2410.21819)).

![Deux juges de familles de modèles différentes notent le même diff. Notes proches : on fait la moyenne. Notes très éloignées (seuil de 25 % d'écart relatif, à titre d'exemple) : un méta-juge lit les preuves, choisit une note et écrit la raison. On ne fait jamais la moyenne de 82 et de 40.](fig4.svg)

Source de la figure : [Zheng et al.](https://arxiv.org/abs/2306.05685) ; [Wataoka et al.](https://arxiv.org/abs/2410.21819). Le seuil de 25 % est un choix d'équipe, pas une norme.

Gardez aussi un humain qui lit le résultat. Dans l'étude de Zheng et al., un juge fort (GPT-4) s'accorde avec les humains plus de 80 % du temps, ce qui laisse des désaccords. Le blind judging évite que le nom de l'outil pèse sur la note.

## Le coût, à côté de la qualité

Un outil bon marché qui demande des sauvetages constants n'est pas bon marché. Notez donc coût et qualité ensemble.

![Plan à deux axes, coût et qualité, avec trois points illustratifs : bon marché et bon ; bon marché mais à sauver ; cher et bon. Une flèche montre qu'un plantage ajoute du coût sans changer la qualité. Aucune donnée : schéma d'idée.](fig5.svg)

Consignez les plantages : ils gonflent le coût sans changer le résultat. Un exemple à petite échelle : l'essai code-graph-pilot (à publier avant ou avec cette page ; section Évaluation) utilise une liste de faits cachée, un juge qui ignore la configuration, et mesure crédits et temps. Il affiche aussi ses limites.

## Ce que ce test ne dit pas

Il ne couvre qu'un code et qu'un relecteur. Les poids de notation sont des choix. Un agent dans le cloud peut être bon sur le processus, la documentation ou la sécurité, que ce test ne mesure pas. Ces résultats ne valent que pour la configuration testée, au moment de la rédaction. Vérifiez tout article plus récent dans ses sources.

## Sources

- OpenAI, why we no longer evaluate SWE-bench Verified : https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- OpenAI, separating signal from noise in coding evaluations : https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- SWE-bench Verified : https://www.swebench.com/verified.html
- Zheng et al., Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena : https://arxiv.org/abs/2306.05685
- Wataoka et al., Self-Preference Bias in LLM-as-a-Judge : https://arxiv.org/abs/2410.21819
- METR, Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity : https://arxiv.org/abs/2507.09089
- METR, We are Changing our Developer Productivity Experiment Design : https://metr.org/blog/2026-02-24-uplift-update/

