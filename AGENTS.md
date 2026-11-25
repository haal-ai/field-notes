# Publishing rules

This repository contains only public-safe publication material. The private research catalogue, source exports, private URLs, credentials, and personal identity records stay outside it.

Use Jean Marin when an individual author is required. Keep real names and employer details out of this publication. Label individual views separately from HAAL publications.

Read `publisher/EDITORIAL.md` before writing. Start from `content/catalogue.json`. Use `python3 build.py` to validate and generate the catalogue, articles, and maintenance ledger. The build output is `_site/`.

Every published page requires a useful explanatory visual and caption. A logo or decorative image does not satisfy this rule. Use readable text, accessible diagrams, quiet colours, and light and dark themes. Public articles need a technical review, a rights and privacy review, and an explicit publication approval. The two initial test pages are approved only as publication-process tests.

News expires three calendar months after first publication. Editing does not reset this date. A guide review is due after six months by default, or three months for fast-changing instructions. A missed review does not prove a guide is wrong. Experiments retain their dates, versions, method, and limitations.

Use the `site` branch for approved releases in this new repository. Push only a named branch. Never push main, mainline, or master, and never change a protected reference through an API. Check the workflow and the public URL after a release. Record the commit and observed deployment outcome. Do not report success from a push receipt alone.

The scheduled GitHub workflow refreshes age labels and the maintenance ledger. It does not use an LLM, change approval status, write articles, or declare a technical review complete.

