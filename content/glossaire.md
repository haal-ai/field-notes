# Glossaire

## LLM
match: LLMs?
Un LLM (large language model) est un grand modèle de langage : un programme qui a appris à prédire la suite d'un texte. Il écrit sa réponse un token à la fois.

## GPU
match: GPUs?
Le GPU est la puce graphique qui fait presque tout le calcul d'un modèle. Sa mémoire est limitée, ce qui explique la plupart des contraintes décrites ici.

## token
Un token est un petit morceau de texte : un mot, un bout de mot ou un signe. Le modèle lit et écrit des tokens, pas des lettres.

## tokenizer
Le tokenizer est le programme qui coupe un texte en tokens avant que le modèle le lise. Le découpage dépend du tokenizer choisi.

## prompt
Le prompt est le texte qu'on donne au modèle : la question, les consignes, le contexte. Le modèle écrit sa réponse à partir de lui.

## embedding
match: embeddings?
Un embedding est la liste de nombres (un vecteur) qui représente un token pour le modèle. Le modèle calcule avec ces vecteurs, jamais avec les lettres.

## attention
L'attention est le mécanisme qui laisse chaque token regarder les tokens précédents pour choisir ce qui compte. Elle produit pour chaque token une query, une key et une value.

## query, key, value
match: quer(?:y|ies)|keys?|values?
Pour chaque token, le modèle calcule trois vecteurs notés Q, K et V. La query (Q) dit ce que le token cherche ; la key (K), ce qu'il propose ; la value (V), le contenu à transmettre.

## KV head
match: KV heads?
Une KV head est le couple de key et de value (K et V) d'une attention head. Avoir moins de KV heads que de queries réduit la taille du KV cache.

## KV cache
match: KV caches?
Le KV cache garde les keys et les values (K et V) de chaque token déjà traité, pour ne pas les recalculer à chaque étape. Il grandit avec la longueur du contexte et occupe beaucoup de mémoire GPU.

## prefill
Le prefill est la première phase : le modèle lit tout le prompt d'un coup et remplit le KV cache. Il est surtout limité par le calcul.

## decoding
Le decoding est la phase où le modèle écrit la réponse, un token par étape. Chaque étape relit le KV cache, ce qui rend cette phase surtout limitée par la mémoire.

## speculative decoding
Le speculative decoding fait proposer plusieurs tokens par un petit modèle, que le grand modèle vérifie en parallèle. La distribution de sortie du grand modèle ne change pas.

## batching
match: continuous batching|batching|batch(?:es)?
Le batching consiste à traiter plusieurs requêtes ensemble pour mieux occuper le GPU. Avec le continuous batching, une requête terminée est remplacée tout de suite par une requête en attente.

## logits
Les logits sont les scores bruts que le modèle donne à chaque token possible du vocabulaire, avant le choix du suivant.

## latency
La latency est le temps d'attente. Entre deux tokens, c'est le temps d'une étape de decoding ; avant le premier token, c'est surtout le temps du prefill.

## throughput
Le throughput est la quantité de travail faite par seconde, par exemple le nombre de tokens produits par seconde pour l'ensemble des requêtes. Il ne dit rien de la latency d'une requête seule.

## memory bandwidth
match: memory bandwidth|bandwidth
La memory bandwidth est le nombre d'octets que la puce peut lire en mémoire par seconde. Quand la lecture limite la vitesse, on dit que le travail est limité par la mémoire.

## weights
match: weights?
Les weights sont les nombres appris par le modèle : ils forment l'essentiel de sa taille. Un modèle de 7 milliards de weights en compte 7 milliards.

## activations
match: activations?
Les activations sont les nombres calculés à partir de votre entrée pendant l'exécution du modèle. Contrairement aux weights, elles changent à chaque requête.

## quantization
La quantization range les weights avec moins de bits (par exemple 4 au lieu de 16) pour gagner de la mémoire. Le prix : un peu de précision.

## dequantization
La dequantization est l'opération inverse : retrouver une valeur approchée à partir de l'entier stocké, en le multipliant par le scale. Le résultat n'est jamais exactement l'original.

## scale
match: scales?
Un scale est le nombre par lequel on divise un groupe de weights avant d'arrondir, et par lequel on multiplie ensuite pour revenir. Chaque groupe a son propre scale.

## zero-point
match: zero-points?
Le zero-point est un décalage qui déplace la plage des entiers stockés. Certains formats l'ajoutent au scale pour mieux couvrir les valeurs d'un groupe.

## fine-tuning
Le fine-tuning prolonge l'entraînement d'un modèle sur des données précises pour l'adapter à une tâche.

## code graph
match: code graphs?
Un code graph est un index d'un projet de code : définitions, appelants, types et routes. Un agent peut l'interroger au lieu de lire les fichiers un par un.

## agent
match: agents?
Un agent est un programme qui lance des outils (recherche, lecture de fichiers, commandes) pour le compte d'un modèle de langage.

## FP16, FP8, bf16, int8
match: FP16|FP8|FP4|bf16|int8|int4
Formats de nombres de 16, 8 ou 4 bits. FP16, FP8 et bf16 sont des nombres à virgule ; int8 et int4 sont des entiers. Moins il y a de bits, moins il faut de mémoire.

## MCP
Le MCP (Model Context Protocol) est un protocole ouvert qui relie un agent à des outils et à des sources de données.

## context window
Le context window est la quantité maximale de tokens qu'un modèle lit en une fois.

## time to first token
Le time to first token est le délai entre l'envoi d'une requête et l'apparition du premier token de réponse.

## MoE (mixture-of-experts)
match: MoE|mixture-of-experts
Un modèle MoE (mixture-of-experts) a, dans chaque couche, plusieurs blocs de calcul appelés experts. Il n'en utilise que quelques-uns pour chaque token. Le modèle peut ainsi avoir beaucoup de paramètres sans tous les calculer à chaque fois.

## open-weight
Un modèle open-weight a ses weights publiés et téléchargeables, à la différence d'un modèle fermé accessible seulement par une API.

## checkpoint
Un checkpoint est un fichier, ou un ensemble de fichiers, qui contient les weights d'un modèle à un moment donné de son entraînement.

## skill
match: skills?
Une skill est un ensemble d'instructions et de fichiers qu'un agent charge pour une tâche précise.

## hook
match: hooks?
Un hook est un petit programme déclenché automatiquement à un moment précis du travail d'un agent.

## harness
Le harness est le logiciel qui entoure un modèle pour en faire un agent : outils, boucle d'exécution, permissions.

## sandbox
Une sandbox est un environnement isolé où un agent exécute des commandes sans toucher au reste du système.

## worktree
match: worktrees?
Un worktree (Git) est une copie de travail supplémentaire d'un même dépôt, sur une autre branche que la copie principale.

## preview
Une preview est une version anticipée d'un produit ou d'un modèle, pas encore stable ni complète.

## GA
match: \bGA\b
GA (disponibilité générale) désigne une version considérée stable et complète, ouverte à tous les clients, après la preview.

## benchmark
match: benchmarks?
Un benchmark est un test standardisé qui mesure la performance d'un modèle ou d'un outil.

## disaggregated serving
Le disaggregated serving fait tourner le prefill et le decoding (aussi appelé decode) sur des machines séparées.

## forward pass
match: forward passe?s?
Un forward pass est un passage complet d'une entrée à travers le modèle.

## expert
Un expert est l'un des blocs de calcul d'une couche MoE. Il est appris à l'entraînement. Ce n'est pas forcément un spécialiste d'un sujet.

## router
Le router est un petit réseau qui donne un score à chaque expert pour un token donné. Ces scores servent à choisir les experts et à pondérer leurs sorties.

## top-k
Le top-k garde les k experts qui ont les meilleurs scores et ignore les autres. Mixtral garde par exemple 2 experts sur 8.

## active parameters
Les active parameters sont la part du modèle réellement utilisée pour un token. Dans un MoE, ils sont bien moins nombreux que les paramètres totaux.

## load balancing
Le load balancing est une méthode d'entraînement qui évite que quelques experts reçoivent presque tous les tokens. Il répartit le travail entre tous les experts.

## hit, miss, hit rate
match: hit rate|hit|miss
Un hit veut dire que l'expert demandé est déjà en mémoire rapide. Un miss oblige à le lire sur un stockage plus lent, comme un SSD. Le hit rate est la part des demandes servies par un hit.

## SSD, NVMe, RAM, VRAM
match: SSD|NVMe|RAM|VRAM
Un SSD (ici NVMe) est un stockage rapide, mais bien plus lent que la RAM pour lire des weights. La RAM est la mémoire de la machine. La VRAM est celle de la carte GPU.

## auxiliary loss
Une auxiliary loss est un terme ajouté à la fonction de perte pendant l'entraînement, pour imposer une contrainte annexe, par exemple répartir les tokens entre les experts.

## SKILL.md
match: SKILL\.md
Le SKILL.md est le fichier principal d'une skill. Il commence par un frontmatter (name, description), puis donne les instructions en Markdown. C'est le seul fichier obligatoire.

## frontmatter
match: frontmatter
Le frontmatter est l'en-tête de métadonnées placé au début d'un fichier Markdown, entre deux lignes `---`. Dans une skill, il contient le name et la description.

## progressive disclosure
match: progressive disclosure
La progressive disclosure est un chargement par étapes. L'agent lit d'abord le nom et la description, puis les instructions si la tâche correspond, puis les fichiers annexes seulement au besoin.

## library skill
match: library skills?
Une library skill est une skill écrite par les mainteneurs d'une bibliothèque et publiée dans son paquet. Elle décrit donc la version installée. C'est une convention proposée, pas un standard.

## dependency
match: dependenc(?:y|ies)|dépendances?
Une dependency est une bibliothèque dont un projet a besoin. Elle est « directe » quand le projet la déclare lui-même.

## approval
match: approvals?
L'approval est la décision explicite de l'utilisateur d'accepter la skill d'un paquet. Avec pnpm, elle s'enregistre dans le projet (`pnpm approve`) ; sans elle, rien n'est lié à l'agent.

## symlink
match: symlinks?
Un symlink est un lien qui fait apparaître un fichier ou un dossier à un deuxième endroit, sans le copier. pnpm s'en sert pour relier une skill de node_modules au dossier de l'agent.

## supply chain
match: supply chain
La supply chain est tout ce que votre projet reçoit de tiers : code, mais aussi instructions et scripts. Une skill d'un paquet en fait partie.

## Git
Git est le système qui garde l'historique d'un code. Chaque copie contient tout cet historique.

## repository
match: repositor(?:y|ies)|dépôts?
Un repository (dépôt) est le dossier suivi par Git, avec tout son historique.

## commit
match: commits?
Un commit est un enregistrement daté d'un ensemble de modifications du code.

## branch
match: branch(?:es)?
Une branche est une ligne de travail nommée, qui pointe vers un commit. La branche principale s'appelle souvent main.

## ref
match: refs?
Une ref est le pointeur nommé (une branche ou un tag) qui désigne un commit. Déplacer une branche, c'est changer sa ref.

## push
match: push(?:es)?
Un push envoie de nouveaux commits au serveur, puis déplace une branche. C'est un geste que les agents répètent très souvent.

## clone
match: clon(?:e|es|er)
Un clone est la copie complète d'un repository sur une machine. Un agent dans le cloud en refait un à chaque tâche.

## content-addressed
Un objet content-addressed (adressé par son contenu) est nommé par l'empreinte de son contenu. Il ne change donc jamais, et plusieurs machines peuvent le stocker sans se mettre d'accord.

## replica
match: replicas?
Un replica est une copie complète d'un repository sur un autre serveur. Plusieurs replicas protègent contre la perte d'une machine.

## quorum
Le quorum est la majorité de replicas qui doivent être d'accord avant qu'une écriture soit validée.

## lock
match: locks?
Un lock est un verrou : il laisse une seule écriture à la fois passer. Les autres attendent leur tour.

## compare-and-swap
Un compare-and-swap est une mise à jour qui réussit seulement si la valeur actuelle est celle qu'on attendait. Sinon, elle échoue et on recommence.

## write-ahead log
Un write-ahead log est un journal où l'on écrit chaque changement d'abord, avant tout le reste. En cas de panne, on le relit pour retrouver l'état.

## object storage
Un object storage est un stockage en ligne de fichiers (de type S3). Il est durable et peu cher, mais plus lent qu'un disque local.

## CI
match: \bCI\b|continuous integration
La CI (continuous integration) est l'ensemble des vérifications automatiques lancées à chaque changement de code : build, tests. Un changement n'est accepté que si elles réussissent.

## merge queue
match: \bmerge queues?\b|\bmerge trains?\b
Une merge queue (ou merge train) est une file qui teste chaque changement avec ceux qui le précèdent avant de le fusionner. Si un test échoue, les changements suivants repartent.

## pull request
match: \bpull requests?\b
Une pull request est une demande de fusion d'un changement de code dans la branche principale. Elle permet la relecture et lance la CI.

## retrieval
match: retrieval
Le retrieval est l'étape qui retrouve, dans une grande masse de documents, ceux qui répondent à une question. On l'utilise avant de donner du texte à un LLM, ou pour chercher directement.

## keyword search
match: keyword search
La keyword search est la recherche par mots exacts. Un index note dans quels documents chaque mot apparaît. Elle trouve bien les codes et les noms précis, mais pas les formulations différentes.

## BM25
match: BM25
La BM25 est la formule de classement classique de la keyword search. Elle favorise les mots rares et ceux qui reviennent souvent dans un document.

## vector search
match: vector search|dense retriever
La vector search est la recherche par le sens. Chaque texte devient un embedding, et on garde les textes dont l'embedding est le plus proche de celui de la question. Elle trouve des formulations différentes, mais peut manquer un code exact.

## graph
match: graph databases?|\bgraphs?\b
Un graph stocke des éléments (nœuds) et leurs liens (arêtes). Il sait suivre ces liens, par exemple pour trouver tout ce qui dépend d'un fournisseur. La similarité seule ne le fait pas.

## hybrid search
match: hybrid search|hybrid retrieval
Le hybrid search combine plusieurs méthodes, par exemple mots exacts et sens, puis fusionne les listes de résultats. Il aide souvent en moyenne, mais peut aggraver certaines requêtes.

## RRF
match: RRF
La RRF (reciprocal rank fusion) fusionne des listes classées. Chaque document reçoit 1 / (k + rang) dans chaque liste, puis on additionne les scores. Avec k = 60, valeur proposée par les auteurs de la méthode, un premier rang vaut 1/61.

## RAG
match: \bRAG\b
Le RAG (retrieval-augmented generation) retrouve des passages utiles, puis les donne au LLM avec la question. Le modèle répond à partir de ces passages.

## GraphRAG
match: GraphRAG
Le GraphRAG est un RAG qui s'appuie aussi sur un graph de liens entre éléments, en plus de la recherche par le sens.

## nDCG@10
match: nDCG@10
Le nDCG@10 est une note de qualité d'un classement. Elle récompense les bons documents placés tout en haut des 10 premiers résultats. Déjà présents dans le glossaire (non redéfinis) : embedding, benchmark, LLM, code graph, context window.

## diff
match: diffs?
Un diff est la liste des lignes ajoutées et supprimées par un changement de code. Il montre ce que l'agent a modifié, sans le code déjà présent.

## LLM judge
match: LLM judges?
Un LLM judge est un LLM qui note la réponse d'un autre modèle ou outil à partir d'une grille. Il va vite, mais il a des biais, par exemple pour les réponses longues.

## blind judging
match: blind judging
Le blind judging est une notation faite sans savoir quel outil ou quel modèle a produit le résultat. Il évite que le nom de l'outil influence la note.

## contamination
match: contamination
La contamination désigne le cas où un modèle a déjà vu les problèmes d'un test, ou leurs solutions, pendant son entraînement. Son score est alors trop flatteur.

## self-preference bias
match: self-preference bias
Le self-preference bias est la tendance d'un LLM judge à mieux noter les textes proches de ceux qu'il écrirait lui-même. C'est pourquoi on prend deux juges de familles différentes.

## inference server
match: inference servers?
Un inference server charge un modèle sur un GPU et répond aux requêtes. Il gère le batching et le KV cache. vLLM et SGLang en sont des exemples.

## API gateway
match: API gateways?
Une API gateway est un service placé devant les modèles. Elle offre une adresse unique, gère les clés et le routage, et peut basculer vers un autre serveur en cas de panne.

## ACP
match: ACP|Agent Client Protocol
L'ACP (Agent Client Protocol) est un protocole ouvert qui décrit comment un client, comme un éditeur ou un IDE, pilote un agent de code. Il joue un rôle proche de celui de LSP pour les serveurs de langage. Il ne choisit ni le modèle, ni la connexion, ni la facturation.

## API compatible OpenAI
match: API HTTP compatible OpenAI|API compatible OpenAI
Une API compatible OpenAI accepte les mêmes requêtes HTTP que celle d'OpenAI. Les outils changent de serveur en changeant seulement l'adresse.

## supply chain attack
match: supply chain attacks?
Une supply chain attack piège un paquet ou un outil que d'autres installent. Tout ce qui l'installe est alors touché.

## oracle
match: oracles?
Un oracle est l'observation qui sert à juger le résultat d'un test. On la fixe avant le test : un compteur, un journal de requêtes. Sans oracle défini d'avance, on interprète le résultat après coup.

## observer
match: observers?
Un observer est le composant qui enregistre ce qui s'est vraiment passé. Il travaille hors de la réponse du modèle. Il ne croit pas ce que le modèle affirme.

## driver
match: drivers?
Un driver est le script ou le navigateur piloté qui envoie les requêtes au produit testé. Il note aussi les événements. Il ne juge pas le résultat.

## testing agent
match: testing agents?
Un testing agent est l'agent qui prépare et organise les vérifications. Il collecte et compare des preuves. Il ne décide ni du périmètre ni du déploiement : ce sont des personnes.

## fixture
match: fixtures?
Une fixture est un jeu de données ou de pages fictives, préparé pour un test. Elle ne contient rien de réel. Si elle est cassée, le résultat du test ne prouve rien.

## guardrail
match: guardrails?
Un guardrail est une règle appliquée par le système lui-même, pas par le modèle. Elle autorise ou refuse une action. C'est lui qu'on cherche à observer pour parler d'enforcement.

## enforcement
match: enforcement
L'enforcement est le blocage réel d'une action par le système. On le constate quand la frontière refuse et qu'un chemin autorisé équivalent aboutit. Un refus du modèle seul n'en est pas la preuve.

## advisory
match: advisor(y|ies)
Un advisory est une fiche publique qui décrit une faille connue et les versions touchées. Une correspondance ne prouve pas que la faille est exploitable chez vous.

## AISVS
match: AISVS
AISVS (AI Security Verification Standard) est un standard ouvert de l'OWASP. Il liste des exigences de sécurité testables pour les applications d'IA, classées en trois niveaux. Il ne délivre pas de certificat.

## AICM
match: AICM
L'AICM (AI Controls Matrix) est une liste de contrôles de sécurité pour les services d'IA, publiée par la Cloud Security Alliance (CSA). Elle se télécharge librement.

## AIUC-1
match: AIUC-1
AIUC-1 est un standard d'audit et de certification pour les agents d'IA. Il comprend des tests techniques et produit un rapport qui indique le périmètre audité.

## OSV
match: OSV
Base ouverte de vulnérabilités connues dans les paquets logiciels. Une API permet de chercher par paquet et par version.

## framework
match: frameworks?
Un framework est un cadre de référence : une liste structurée d'exigences ou de contrôles qu'on peut suivre ou comparer. Il ne remplace pas un test sur votre propre système.

## AI-CAIQ
match: AI-CAIQ
L'AI-CAIQ est le questionnaire standard qu'on pose à un fournisseur de service d'IA. Ses réponses décrivent les contrôles de l'AICM que le fournisseur met en place.

## STAR for AI
match: STAR for AI
STAR for AI est un programme de la CSA. Au niveau 1, le fournisseur s'auto-évalue et publie ses réponses dans un registre public. Au niveau 2, un tiers indépendant évalue.

## control
match: contrôles?|controls?
Un contrôle est une mesure précise qui réduit un risque, par exemple limiter l'accès d'un agent à certains fichiers.

## Statement of Applicability
match: Statement of Applicability
Le Statement of Applicability est la liste, signée par l'auditeur, des exigences et des contrôles réellement audités pour un agent. Il indique aussi les exclusions et leur raison.

## merge
match: \bmerges?\b
Un merge est la fusion de deux séries de changements dans un même code. Un merge propre ne garantit pas que le résultat fonctionne.

## generalist / specialist agents
match: generalist|specialist agents?
Un agent generalist fait tout de bout en bout. Les specialist agents ont chacun un rôle (analyse, code, test) et se passent le travail.

## baseline
match: \bbaselines?\b
Une baseline est la référence à laquelle on compare, par exemple un seul agent avec le même budget de calcul. Sans baseline équitable, un gain peut venir du budget et non de la méthode.

## setup
match: \bsetups?\b
Un setup est la configuration testée : un modèle et un harness, avec leurs réglages. Un résultat ne vaut que pour le setup mesuré.

## runner
match: \brunners?\b
Un runner est la machine qui exécute les vérifications de la CI. On compte ses minutes d'exécution.

## surface
match: surfaces?
Une surface est l'interface qu'une personne utilise pour travailler avec un agent : IDE, éditeur, CLI ou fenêtre d'agents. C'est un terme de travail de cet article.

## AI service
match: AI services?
Un AI service est le compte, le contrat et la route par lesquels on accède aux modèles, avec la facturation. Il est distinct du harness qui fait tourner l'agent. C'est un terme de travail de cet article.

## BYOK
match: BYOK
BYOK (bring your own key) veut dire utiliser sa propre clé d'API chez un fournisseur de modèles, au lieu de la route par défaut du produit. Les limites varient d'un produit à l'autre.

## capability
match: capabilit(y|ies)
Une capability est une fonction qu'un client ou un agent annonce au début d'une connexion. Ce qui n'est pas annoncé est considéré comme non pris en charge.

## JSON-RPC
match: JSON-RPC
Le JSON-RPC est un format de messages en JSON, avec requêtes, réponses et notifications. ACP l'utilise pour les échanges entre client et agent.

## tool calling
match: tool calling
Le tool calling est la capacité d'un modèle à demander l'exécution d'un outil. L'agent exécute l'outil, puis renvoie le résultat au modèle.

## Agent Commander (terme de travail)
match: Agent Commander
Agent Commander est l'étiquette que l'auteur donne à une surface organisée autour de plusieurs agents. Ce n'est pas un terme standard. Il ne désigne pas la fonction « Agent Command Center » de Devin.
