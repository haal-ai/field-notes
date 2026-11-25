# HAAL field notes

A sober, visual library for AI and software engineering knowledge. The initial release contains two explicitly identified publication-process test pages.

## Build locally

Run `python3 build.py`, then `python3 -m unittest discover -s tests -v`. The output is `_site/`. No external Python dependency is required.

For a local HTTP preview, run `python3 -m http.server 8765 --bind 127.0.0.1 --directory _site`.

## Source and maintenance

`content/catalogue.json` is the entry point. It contains approved page metadata, useful visuals, content, publication dates, technical review dates, and revision notes. The build generates complete static article HTML and `maintenance/ledger.json`, with one next action and due date for each article.

`publisher/EDITORIAL.md` contains the writing, source, visual, approval, and maintenance rules. `AGENTS.md` makes those rules visible to repository agents. Private research material stays outside this repository.

The `site` branch is the release source. GitHub Actions builds and deploys Pages on approved pushes and refreshes age labels daily. Pull requests build and check without deploying. Scheduled builds use no LLM. They cannot approve content or record a technical review.

## Publication proof

The first release uses `publication-test-v1`. A second release changes the public trial marker. Creation and update are proven only by reading the corresponding public page after each deployment.

GitHub workflow setup follows [the official Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages). Pages must use GitHub Actions as its publishing source.
