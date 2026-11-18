# pavel-ship-it.github.io

Developer site of Pavel Yakimenko: https://pavel-ship-it.github.io/
Shared support page for all apps: https://pavel-ship-it.github.io/support

Links the app sites:
- Fridge Pick: https://pavel-ship-it.github.io/fridge-pick-support/
- Jewelers Handbook: https://pavel-ship-it.github.io/jewelers-handbook-support/

Sources are in `site/`, the built site is in `docs/` (GitHub Pages: main, /docs).

    pip install jinja2
    python3 site/build.py          # rebuilds docs/
    python3 site/make_images.py    # only to regenerate favicon / OG images (needs Pillow)

App list, store links and email are in `site/config.json`. The build fails if Russian text appears on a
page. `docs/robots.txt` is the root robots.txt for the whole host, so it lists this sitemap and both app sitemaps.
