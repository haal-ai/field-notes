# Colibri : un moteur d'inférence qui lit les experts sur disque

## L'essentiel

- Colibri est un inference engine open source, écrit en C. Il vise les très gros modèles MoE sur une machine locale, à condition que le disque puisse contenir le modèle.
- Son idée : le modèle n'a pas besoin de tenir en mémoire. Les experts rares restent sur NVMe et sont lus à la demande.
- Le prix est la vitesse. Les chiffres cités viennent du projet lui-même, au 27 novembre 2026, sur des machines différentes.

## Où il se place

Colibri est une couche de local inference : il charge un modèle et le fait tourner sur votre machine. Il fait partie de la couche modèle. Il offre une API compatible OpenAI et un serveur MCP : tout programme qui sait appeler un modèle local peut donc l'utiliser.

![Colibri tourne sur votre machine, dans la couche modèle : il charge les weights et offre une API compatible OpenAI et un serveur MCP à tout programme qui l'appelle.](fig1.svg)

Le projet est individuel, sous licence Apache 2.0 pour le code. Chaque modèle garde sa propre licence. La dernière version, la v2.2.0, date du 22 novembre 2026. Source de la figure : [README du projet](https://github.com/JustVugg/colibri) et [releases](https://github.com/JustVugg/colibri/releases).

## Le problème : gros sur disque, petit par token

La note « MoE : comment un token choisit ses experts » explique le mécanisme. Ici, on retient une seule conséquence : un modèle MoE est énorme sur disque, mais peu de ses weights servent à chaque token. Exemple donné par le README : GLM-5.2 compte 744 milliards de paramètres, environ 40 milliards actifs par token, et seulement 11 Go environ changent d'un token au suivant.

![Barres : 744 milliards de paramètres au total, environ 40 milliards actifs (5,4 %), environ 11 Go qui changent d'un token au suivant. Chiffres du README, exemple GLM-5.2.](fig2.svg)

Source de la figure : [README du projet](https://github.com/JustVugg/colibri). Le pourcentage est un calcul : 40 / 744.

Le modèle doit donc être placé, pas forcément logé en entier dans la RAM.

## Trois niveaux de mémoire

Colibri range le modèle selon l'usage. La partie dense (attention, experts partagés, embeddings) reste en RAM ; le README indique que, s'il y a un GPU, elle peut aussi y aller. Les experts chauds vont sur le GPU s'il y en a un. Les tièdes restent en RAM. Les froids sont lus sur NVMe, avec un cache qui apprend quels experts la charge réclame.

![Trois niveaux : GPU (experts chauds), RAM (partie dense et experts tièdes), NVMe (experts froids). Une flèche part du router vers l'expert demandé ; un miss descend lire le NVMe. Aucune vitesse n'est représentée.](fig3.svg)

Source de la figure : [README du projet](https://github.com/JustVugg/colibri), section « how it works ».

Le projet affirme que ce placement change la vitesse, pas le résultat : mêmes weights, mêmes décisions du router, pas de changement silencieux de précision. C'est une affirmation du projet, que cette page n'a pas vérifiée.

## Ce que cela donne en vitesse

Le README publie des mesures de decoding pour GLM-5.2, sur le matériel de l'auteur. Le 9,0 à 9,2 tok/s demande un réglage précis : tous les experts résidents en mémoire et un entrelacement NUMA sélectif. Sans ce réglage, le README donne 5,8 à 6,8. Le 1,83 est mesuré à chaud, sur CPU seul.

![Vitesse de decoding en tok/s, mesures de l'auteur : 0,05 à 0,1 sur un portable de 25 Go de RAM (cache froid) ; 1,83 sur une machine de 128 Go (Ryzen AI Max+), à chaud, CPU seul ; 9,0 à 9,2 sur 6 GPU RTX 5090 avec réglage NUMA et experts résidents (5,8 à 6,8 sans). Matériel différent : les barres ne sont pas comparables entre elles.](fig4.svg)

Source de la figure : [README du projet](https://github.com/JustVugg/colibri) (auto-déclaré, aucune mesure indépendante trouvée).

Lecture : sur un portable, le résultat est utilisable pour essayer, pas pour converser. Le débit monte avec la mémoire et les GPU disponibles. Un modèle plus petit va plus vite : Qwen3.6-35B-A3B atteint 30,0 tok/s avec CUDA (machine C du README, un RTX 3070 de 8 Go ; auto-déclaré).

## Du démarrage au serveur local

Au premier lancement, Colibri mesure la machine : RAM, disque, GPU. Il estime la vitesse de decoding, recommande un modèle, le télécharge et le sert en local. Le projet compte 20 tok/s comme fluide, et la lecture sur disque pour moitié.

![Cinq étapes : détecter RAM, disque et GPU ; estimer la vitesse ; recommander un modèle ; télécharger ; servir sur une adresse locale compatible OpenAI.](fig5.svg)

Source de la figure : [README du projet](https://github.com/JustVugg/colibri).

## Face aux autres moteurs

Colibri n'est pas un inference server de data-centre comme vLLM ou SGLang (voir la note sur ces deux outils). Il ne se présente pas non plus comme un simple emballage comme Ollama. Les alternatives proches pour une machine locale sont llama.cpp, avec le format GGUF et le partage du travail entre CPU et GPU, et les projets qui déportent les experts vers le disque. La différence annoncée est de traiter la lecture des experts sur disque comme un niveau de mémoire à part entière. Aucune comparaison indépendante n'a été trouvée : cette page ne dit pas qu'il va plus vite qu'un autre.

## Limites

- Toutes les vitesses sont auto-déclarées, sur des machines différentes.
- Le disque doit contenir le modèle : GLM-5.2 pèse 429 Go à télécharger. Le minimum du projet est 8 Go de RAM, pour le plus petit modèle. « Machine ordinaire » ne veut pas dire que tout tient partout.
- La qualité d'un modèle en int4 lu en streaming n'est pas testée ici.
- Le projet change chaque semaine : modèles, backends (CPU, Vulkan, CUDA) et réglages.
- Le moteur est sous Apache 2.0 ; chaque modèle a sa licence.

Ceci n'est pas une recommandation d'usage.

## Sources

- Colibri, README du projet (consulté le 2026-11-27) : https://github.com/JustVugg/colibri
- Colibri, releases (v2.2.0, 2026-11-22) : https://github.com/JustVugg/colibri/releases
