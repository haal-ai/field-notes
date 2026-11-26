# Surface, harness, AI service et ACP : où s'arrête l'interchangeabilité

## L'essentiel

- Quand on dit « j'utilise tel outil », on regroupe trois choses : la surface, le harness et l'AI service.
- ACP sépare la surface du harness pour les agents de code. Il laisse de côté le fournisseur de modèle, la connexion, la facturation et le sandbox.
- « Agent Commander » est une étiquette de l'auteur pour une surface pensée autour de plusieurs agents. Ce n'est pas un terme standard, et ce n'est pas l'« Agent Command Center » de Devin, qui est le nom d'une fonction de ce produit.

Lecture de la documentation publique faite le 2026-11-26. Rien n'a été exécuté ni testé. Les pages des éditeurs changent vite : relisez-les avant de vous y fier.

## Trois choix, pas un seul

Les mots surface et harness sont des termes de travail ; « harness » est aussi employé par certains éditeurs. La surface est ce que la personne utilise : IDE, éditeur, CLI, fenêtre d'agents. Le harness est le programme qui fait tourner l'agent, appelle les outils et applique les permissions. L'AI service est le compte, le contrat et la route vers le modèle, avec la facturation. La documentation de Zed décrit cette répartition : l'agent externe garde son runtime, sa connexion, son choix de modèle et ses outils.

![Trois choix empilés : la surface, le harness et l'AI service. ACP relie la surface au harness. L'API du fournisseur relie le harness à l'AI service, hors ACP.](fig1.svg)

Source de la figure : [Zed, External Agents](https://zed.dev/docs/ai/external-agents) ; [ACP, introduction](https://agentclientprotocol.com/get-started/introduction).

Ces trois choix peuvent donc se faire séparément. Ils ne se remplacent pas tous de la même façon.

## Une session ACP

ACP (Agent Client Protocol) décrit comment un client pilote un agent de code. L'idée ressemble à celle de LSP pour les serveurs de langage. En local, l'agent tourne comme un sous-processus et échange en JSON-RPC. Les agents distants sont encore en cours de travail, d'après la documentation.

![Une session ACP en version 1 : initialize, réponse, session/new, session/prompt, flux de session/update, demande de permission si besoin, fin de tour. L'agent parle aussi à des serveurs MCP et à un fournisseur LLM, hors ACP.](fig2.svg)

Source de la figure : [ACP, vue d'ensemble v1](https://agentclientprotocol.com/protocol/v1/overview) ; [ACP, initialisation v1](https://agentclientprotocol.com/protocol/v1/initialization).

À l'ouverture, chaque côté annonce ses capabilities. Ce qui n'est pas annoncé est considéré comme non pris en charge. La v1 est la base stable. La v2 est en Preview : elle retire par exemple les méthodes de fichiers et de terminal côté client. Le contrat lui-même bouge encore.

## Ce qu'ACP standardise, et le reste

ACP couvre une seule frontière. Les extensions sont permises (`_meta`, méthodes préfixées par `_`) : une fonction propre à un éditeur n'est pas portable si l'autre côté l'ignore. MCP est un protocole séparé, qui donne des outils et des données à l'agent. ACP ne définit pas non plus le choix du fournisseur LLM. Une proposition existe, en brouillon seulement. ACP ne place pas l'agent dans un sandbox : les demandes de permission sont indicatives, et le harness reste responsable.

![Deux colonnes. Standardisé : messages client-agent, négociation de version et de capabilities, flux de mises à jour, demandes de permission, transmission des serveurs MCP. Non standardisé : fournisseur LLM (proposition en cours), connexion et facturation, outils propres à l'agent, extensions, sandbox et skills (hors périmètre ACP, lecture de l'auteur).](fig3.svg)

Source de la figure : [ACP, sécurité v1](https://agentclientprotocol.com/protocol/v1/security) ; [ACP, extensibilité v1](https://agentclientprotocol.com/protocol/v1/extensibility) ; [RFD fournisseurs LLM](https://agentclientprotocol.com/rfds/custom-llm-endpoint) ; [ACP, migration v2](https://agentclientprotocol.com/protocol/v2/migration).

La connexion et la facturation restent chez l'agent. Dans Zed, la clé d'API de l'agent maison ne configure pas Claude Agent ni Codex. Dans JetBrains, les agents ACP n'exigent pas d'abonnement JetBrains AI. Dans Devin Desktop, avec un agent ACP tiers, la facturation se fait directement auprès de son fournisseur, d'après la documentation.

## Qui peut héberger qui

Le choix existe dans les deux sens. Un agent peut servir plusieurs clients, et un client peut héberger plusieurs agents.

![Matrice client par agent. Zed : Codex, Claude Agent, OpenCode et Copilot sont listés. Devin Desktop : Codex, Claude Agent et OpenCode sont listés. JetBrains : OpenCode apparaît dans un exemple de configuration. Les autres cases sont « non vérifié ». « Listé » ne veut pas dire « testé ici ».](fig4.svg)

Source de la figure : [Zed](https://zed.dev/docs/ai/external-agents) ; [Devin Desktop](https://docs.devin.ai/desktop/acp) ; [JetBrains](https://www.jetbrains.com/help/ai-assistant/acp.html) ; [liste des agents ACP](https://agentclientprotocol.com/get-started/agents).

Une case « non » veut dire non vérifié, pas impossible.

## Séparer le harness du service d'IA

Plusieurs produits permettent d'amener sa propre clé (BYOK) ou un autre fournisseur, avec des limites différentes.

![Quatre produits. Copilot CLI : fournisseurs compatibles OpenAI, azure et anthropic ; le modèle doit gérer le tool calling et le streaming. OpenCode : catalogue, fournisseur compatible OpenAI, baseURL modifiable. Claude Code : déploiement via Anthropic, Amazon Bedrock, Google Cloud ou Microsoft Foundry : la page compare où l'inférence s'exécute. Cursor : clés pour les modèles de chat seulement, passage par les serveurs de Cursor, la complétion Tab garde les modèles de Cursor. Tout est d'après la documentation du 2026-11-26, non testé.](fig5.svg)

Source de la figure : [Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models) ; [OpenCode](https://opencode.ai/docs/providers/) ; [Claude Code](https://code.claude.com/docs/en/third-party-integrations) ; [Cursor](https://cursor.com/help/models-and-usage/api-keys).

Prudence : comparer une surface seule mélange l'interface, le harness et le modèle. C'est un raisonnement, pas une mesure. Comparez des configurations complètes.

## Sources

- ACP, introduction : https://agentclientprotocol.com/get-started/introduction
- ACP, agents : https://agentclientprotocol.com/get-started/agents
- ACP, protocoles liés : https://agentclientprotocol.com/get-started/related-protocols
- ACP v1, vue d'ensemble : https://agentclientprotocol.com/protocol/v1/overview
- ACP v1, initialisation : https://agentclientprotocol.com/protocol/v1/initialization
- ACP v1, extensibilité : https://agentclientprotocol.com/protocol/v1/extensibility
- ACP v1, sécurité : https://agentclientprotocol.com/protocol/v1/security
- ACP v2, migration : https://agentclientprotocol.com/protocol/v2/migration
- ACP, RFD fournisseurs LLM : https://agentclientprotocol.com/rfds/custom-llm-endpoint
- Zed, External Agents : https://zed.dev/docs/ai/external-agents
- JetBrains, ACP : https://www.jetbrains.com/help/ai-assistant/acp.html
- Devin Desktop, ACP : https://docs.devin.ai/desktop/acp
- GitHub Copilot CLI, BYOK : https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models
- OpenCode, providers : https://opencode.ai/docs/providers/
- Claude Code, déploiements : https://code.claude.com/docs/en/third-party-integrations
- Cursor, clés d'API : https://cursor.com/help/models-and-usage/api-keys
