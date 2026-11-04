# soloAS documentation

English and 中文 sources live in `en/` and `zh/`, with matching page names.
Start with [Requirements](en/requirements.md) / [安装要求](zh/requirements.md).

Build from the repository root with Python 3:

```sh
python3 tools/build_docs.py
```

No Python packages or network access are needed. Output is written to `site/docs/`;
the build also renders the homepages and contributors pages and copies the favicon and custom-domain file into
`site/` for the Pages artifact. The Pages workflow builds this artifact before
deployment. Enabling Pages and publishing remain repository-owner actions.

`template.html` is the single page template. The build reuses the homepage's CSS
custom properties so the docs share its colors and typography. Internal links use site-root paths or relative paths. The language menu and hreflang
alternates are generated from `tools/site_config.json`, with native language names
and a current-language indicator. Add a language there and supply its translated
page sources; English lives at `/`, Simplified Chinese at `/zh/`.

Release support data is stored in `tools/data/site013-release-input.json`.
Use `python3 tools/render_support.py --check` to verify the generated support list. See `tools/README.md` for synchronization.

The small Markdown renderer supports headings with anchors, paragraphs, fenced
code blocks, simple tables, flat ordered and unordered lists, blockquotes,
links, emphasis, inline code and horizontal rules. Supported embedded SVG and HTML blocks are rendered by the site builder. Keep
nested content flat and avoid pipes inside table cells. Relative `.md` links
read correctly on GitHub and become `.html` links in the generated pages.

When editing, update both languages. Add navigation entries in `PAGES` in the
build script when introducing a page. Keep unconfirmed release facts marked
`TODO` until the controller supplies them.

Learning articles are discovered under `docs/{en,zh}/learn/*.md`. Their first H1
is the title; optional front matter `order: 10` controls ordering. The build
generates `learn/index.html` in each language. Place images under
`docs/assets/learn/` and link them relative to the article, for example
`../../assets/learn/figure.png`. The build copies these assets into the artifact.
