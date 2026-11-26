# La chaîne d'une IA open source, de la plateforme au modèle

## L'essentiel

- Faire tourner soi-même un assistant IA, c'est empiler cinq couches. Chacune fait un seul travail.
- Chaque couche parle à la suivante par une interface publique. On peut donc en remplacer une sans toucher aux autres.
- À grande échelle, la mémoire (le KV cache) devient le premier souci. Côté sécurité, le paquet logiciel de la passerelle mérite une vigilance particulière.

## Cinq couches, quatre liaisons

Le modèle open-weight est un fichier de weights. Un inference server le charge sur un GPU et répond aux requêtes. Une API gateway (une passerelle) se place devant et offre une adresse unique. Un harness fait tourner la boucle de l'agent : le LLM choisit une action, le harness l'exécute. Une plateforme de bots, tout en haut, apporte la mémoire, les tâches planifiées et les canaux de discussion.

![Les cinq couches, du modèle à la plateforme de bots, avec l'interface entre chaque couche.](fig1.svg)

Source(s) de la figure : [documentation d'ACP](https://agentclientprotocol.com/overview/introduction) ; [documentation de vLLM](https://docs.vllm.ai/en/latest/serving/online_serving/).

vLLM, un inference server, expose une API HTTP compatible OpenAI, avec par exemple les routes Chat Completions et Responses. Une API gateway qui parle la même API peut donc se placer devant. Côté agent, le protocole ACP relie un éditeur à un agent de code, comme LSP le fait pour les langages. Ici, nous l'étendons à la plateforme, qui joue le rôle du client. En local, l'agent tourne comme un sous-processus et échange en JSON-RPC sur stdio (l'entrée et la sortie standard). Le support des agents distants est, selon ses auteurs, « en cours ».

## Remplacer une couche

Une interface publique rend une couche interchangeable. En principe, changer de serveur revient à changer une adresse dans la configuration. Le nom du modèle change aussi si le serveur le demande.

![Une couche remplacée : seule l'adresse change (et le nom du modèle si le serveur le demande) ; les autres couches ne bougent pas.](fig2.svg)

Source(s) de la figure : [documentation de vLLM](https://docs.vllm.ai/en/latest/serving/online_serving/).

À retenir : l'interface compte plus que le produit. Choisissez-la d'abord, le produit ensuite.

## Un essai sur un portable

Un essai personnel a fait tourner toute la chaîne sur un seul portable Apple, avec un modèle mixture-of-experts en quantization 4 bits, sans appel à un service payant. Un seul client, une seule machine, une seule exécution : c'est une démonstration, pas une mesure. La page ne donne donc aucun chiffre de vitesse.

![Le trajet d'une requête sur le portable : harness, passerelle, serveur, modèle, puis les tokens reviennent en flux.](fig3.svg)

Figure illustrative : aucune source externe, aucun chiffre.

À retenir : une chaîne complète tient sur une machine, à condition de choisir un modèle assez petit. Pour la quantization, voir la note « Quantization : faire tenir un modèle dans moins de mémoire ».

## Ce qui change à grande échelle : la mémoire

Chaque conversation garde son KV cache en mémoire GPU. Sa taille vaut le nombre de tokens multiplié par la mémoire d'un token. Pour Qwen3-30B-A3B, la configuration publique donne 48 couches, 4 KV heads, des têtes de 128 valeurs et du bfloat16 (bf16).

![Taille du KV cache de Qwen3-30B-A3B en bfloat16 : 98 304 octets par token, soit environ 0,8 Go pour 8 192 tokens, 3,2 Go pour 32 768 et 4,0 Go pour 40 960.](fig4.svg)

Source(s) de la figure : [config.json du modèle](https://huggingface.co/Qwen/Qwen3-30B-A3B/raw/main/config.json) (couches, KV heads, taille de tête, type) ; formule : voir la note « Comment un LLM traite un prompt ».

À retenir : le contexte coûte de la mémoire, conversation par conversation. C'est une estimation, sans les optimisations du serveur. Pour la gestion par blocs, voir la note « vLLM et SGLang : deux façons d'économiser la mémoire GPU ».

## Vigilance : la passerelle est un paquet comme un autre

C'est le terrain des supply chain attacks : on piège un paquet que d'autres installent. La passerelle s'installe souvent depuis un index public de paquets, et elle détient les clés d'accès. Si le paquet est piégé, les clés partent avec lui. Le 24 mars 2026, deux versions de LiteLLM (1.82.7 et 1.82.8) ont été publiées sur PyPI avec un voleur d'identifiants. Elles sont restées en ligne environ 40 minutes. Selon LiteLLM, l'image Docker officielle du proxy n'était pas touchée.

![Le risque : un paquet piégé sur un index public s'installe avec la passerelle et lit les clés. Parades : épingler la version, vérifier, construire l'image soi-même.](fig5.svg)

Source(s) de la figure : [LiteLLM, mise à jour de sécurité de mars 2026](https://docs.litellm.ai/blog/security-update-march-2026).

À retenir : épinglez la version de chaque paquet de la chaîne, quel que soit le produit. Construire l'image soi-même est un conseil général, pas un fait de cet incident. L'incident ne dit rien de la qualité du projet ; il vaut pour toute passerelle.

## Et ensuite ?

Sources relues le 26 novembre 2026. Les noms de produits, les versions et ACP changent vite. Cette page décrit la structure, pas un palmarès : vérifiez chaque produit dans sa propre documentation.

## Sources

- Agent Client Protocol, introduction : https://agentclientprotocol.com/overview/introduction
- vLLM, Online Serving : https://docs.vllm.ai/en/latest/serving/online_serving/
- Qwen3-30B-A3B, config.json : https://huggingface.co/Qwen/Qwen3-30B-A3B/raw/main/config.json
- LiteLLM, Security Update (mars 2026) : https://docs.litellm.ai/blog/security-update-march-2026
