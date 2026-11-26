# vLLM et SGLang : deux façons d'économiser la mémoire GPU

Écrit le 25 novembre 2026 d'après vLLM v0.34.0 et SGLang v0.5.23, dernières versions publiées ce jour-là [1][2]. Prochaine relecture dans trois mois.

## En bref

vLLM et SGLang sont deux serveurs open source de grands modèles de langage. Tous deux économisent la mémoire GPU en gérant bien le KV cache. vLLM mise sur l'empaquetage de la mémoire et l'ordonnancement ; SGLang, sur la réutilisation du texte de départ partagé. C'est ma simplification : chaque projet fait aujourd'hui un peu des deux. Le bon choix dépend de votre charge.

SGLang n'a aucun lien avec SLANG, le langage de shaders de NVIDIA et Khronos.

## Le parcours d'une requête

Le serveur reçoit la requête, découpe le texte en tokens, fait tourner le modèle sur le GPU et renvoie les tokens au fil de l'eau [1][2]. Le modèle lit d'abord le prompt : c'est le prefill. Puis il écrit la réponse token par token : c'est le decoding. Une seule étape diffère entre les deux serveurs.

![Parcours d'une requête dans vLLM et SGLang : cinq étapes, dont une seule diffère](fig1.svg)

## Le KV cache coûte cher

Pour chaque token, le modèle garde des résultats intermédiaires. Ce cache évite de tout relire, mais il remplit vite la mémoire. Les auteurs de l'article vLLM ont mesuré que, dans d'anciens serveurs, 20,4 % à 38,2 % seulement de cette mémoire contenaient de vraies données [3]. Mesure des auteurs, sur leurs systèmes.

![Le KV cache : seulement 20,4 % à 38,2 % de la mémoire utile dans d'anciens serveurs](fig2.svg)

## Continuous batching

Les deux serveurs retirent les requêtes finies et ajoutent les requêtes en attente à chaque étape. Le GPU n'attend pas la plus lente. Un batch est l'ensemble des requêtes que le GPU traite ensemble. Le principe vient du système Orca [3]. SGLang le confirme dans son code : son ordonnanceur garde un batch de decoding en cours, commenté « for continuous batching » [4]. Commentaire lu le 25 novembre 2026.

## vLLM : blocs paginés (PagedAttention) et hachage

vLLM découpe le cache en blocs de taille fixe, comme des pages mémoire [3]. Il réutilise les blocs pleins d'un préfixe commun grâce à un hachage [5]. La taille par défaut est passée de 16 à 64 tokens dans la v0.34.0 [1].

![vLLM : blocs paginés, hachage et réutilisation entre requêtes](fig3.svg)

## SGLang : arbre radix (radix tree)

SGLang suppose que beaucoup de requêtes commencent par le même texte. Il le stocke une seule fois dans un arbre radix (RadixAttention) ; chaque requête ne calcule que sa suite [6][7].

![SGLang : un arbre radix, une seule copie du préfixe partagé](fig4.svg)

Le projet annonce des gains jusqu'à 6,4 fois (article d'origine, 2023) ; avec HiCache, un cache à plusieurs niveaux sous la mémoire GPU, jusqu'à 15,5 fois et jusqu'à 6 fois [6][8][9]. Ce sont des cas choisis par le projet, avec leurs réglages. Détail dans la figure 4.

## Les deux projets se rejoignent

vLLM a le cache de préfixes et, en option, un ordre d'admission tenant compte du cache [1]. SGLang peut garder son cache de préfixes au niveau L3 de HiCache pour certains modèles [2]. Le partage ci-dessus est un outil pédagogique, pas un fait sur le code actuel.

## Deux bancs d'essai, deux conclusions

Les tests indépendants sont rares et vieillissent vite. Voici deux tests récents, avec leurs réglages sous la figure 5.

![Deux bancs d'essai qui ne s'accordent pas : Winder.ai et ZenML, avec leurs réglages](fig5.svg)

Sur Llama 3.1 8B, les deux serveurs sont proches [10]. Sur Qwen3.8-27B, Winder.ai mesure SGLang devant vLLM [10] ; ZenML mesure SGLang derrière vLLM [11]. Les charges, versions et réglages diffèrent, avec peu de passes : aucun test ne tranche, et ce n'est pas un classement. Les versions de Winder.ai sont en retard sur les dernières. Je n'ai pas rejoué ces tests.

## Comment choisir

Testez votre charge : part de texte partagé, requêtes simultanées, modèle, matériel. Tout chiffre publié vaut pour une seule configuration.

## Note de statut

Text Generation Inference (TGI) de Hugging Face est en mode maintenance, « as of 12/11/2025 », et recommande vLLM ou SGLang [12]. SGLang vient de LMSYS, qui a annoncé un consortium SGLang le 12 novembre 2026 [13].

## Ce que je n'ai pas vérifié

Je n'ai ni fait tourner ces serveurs ni lu leur code, hors le commentaire d'ordonnanceur [4]. Les chiffres viennent des sources. Les valeurs par défaut changent d'une version à l'autre.

## Sources

1. [vLLM v0.34.0, notes de version](https://github.com/vllm-project/vllm/releases/tag/v0.34.0) ; [dépôt vLLM](https://github.com/vllm-project/vllm)
2. [SGLang v0.5.23, notes de version](https://github.com/sgl-project/sglang/releases/tag/v0.5.23) ; [dépôt SGLang](https://github.com/sgl-project/sglang)
3. Kwon et al., 2023, [article vLLM](https://arxiv.org/abs/2309.06180) ([PDF](https://arxiv.org/pdf/2309.06180))
4. [scheduler.py](https://raw.githubusercontent.com/sgl-project/sglang/main/python/sglang/srt/managers/scheduler.py), commentaire lu le 25 novembre 2026
5. [Page de conception vLLM, cache de préfixes](https://docs.vllm.ai/en/stable/design/prefix_caching/)
6. [Article SGLang](https://arxiv.org/abs/2312.07104)
7. [Billet LMSYS, 2024](https://www.lmsys.org/blog/2024-01-17-sglang/)
8. [Blog SGLang, HiCache](https://www.sglang.io/blog/hicache)
9. [LMSYS, HiCache, 2025](https://lmsys.org/blog/2025-09-10-sglang-hicache/)
10. [Winder.ai](https://winder.ai/vllm-vs-ollama-vs-sglang-llm-inference-comparison/) ; [banc d'essai](https://github.com/winderai/llm-inference-benchmark)
11. [ZenML](https://www.zenml.io/benchmarks/sglang-vs-vllm)
12. [Documentation Inference Endpoints, TGI](https://huggingface.co/docs/inference-endpoints/engines/tgi)
13. [Annonce du consortium SGLang](https://lmsys.org/blog/2026-11-12-sglang-consortium)
