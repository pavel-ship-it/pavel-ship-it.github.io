# Pavel Yakimenko developer site: features

Public site at [https://pavel-ship-it.github.io](https://pavel-ship-it.github.io). This file lists what the site does today, written from the code on `main`. It lives at the repository root so it is visible on GitHub; GitHub Pages serves `main:/docs`, so this file is not part of the website.

The site is generated from `site/` into `docs/` by `python3 site/build.py` (Jinja). `docs/` is the published output and is not edited by hand.

## Implemented features

### Pages and structure

| # | Feature |
|---|---|
| 1.1 | Home page (`/`): introduces Pavel Yakimenko as an indie developer, with a short lead, links to the app list and support, and the app icons. |
| 1.2 | App list on the home page: a card for each app in `site/config.json` (Fridge Pick, Jewelers Handbook, Lightwhirl). Each card has the icon, name, platforms, a short description, store badges, a link to the app website, and a link to that app’s privacy policy. A user-manual link is shown when the app has one. |
| 1.3 | Shared support page (`/support`): one support channel for all apps. Contact email (`dreamcomenull@gmail.com`), a pre-filled mailto button per app, a “what to include” checklist (app and version, device, system version, steps, screenshot), per-app links to the manual (when present), support/FAQ and privacy policy, and a short FAQ. The page says replies are in English or Russian. |
| 1.4 | Shared privacy page (`/privacy`): a short common statement (the apps collect no personal data, have no accounts, ads or tracking, and keep what you enter on the device) and a link to each app’s own privacy policy. |
| 1.5 | 404 page for unknown paths. |
| 1.6 | Canonical URLs without a `.html` suffix (`/support`, `/privacy`). GitHub Pages also serves the `.html` files. |
| 1.7 | Site navigation and footer: Home, Apps, Support, Privacy; a short tagline; a contact line. |
| 1.8 | `robots.txt` at the host root allows crawling and lists this site’s sitemap plus the Fridge Pick and Jewelers Handbook support sitemaps. The 404 page is marked `noindex`. |
| 1.9 | Open Graph / social image for English pages, favicon and apple-touch-icon, and JSON-LD (`Person`, `Organization`, `WebSite`, and a `SoftwareApplication` for each app). Contact points list English and Russian as available languages for email support. |

### Apps and store links

Store URLs come from `site/config.json`. A missing URL is shown as a “Coming soon” badge, not as a link. Lightwhirl’s badge uses the name “Mac App Store”; the others use “App Store”. Google Play badges appear only when the app entry has a `google_play` key (Fridge Pick does; the Play link is not live yet).

| App | Website | Stores today |
|---|---|---|
| Fridge Pick: Quick Meal Ideas (iPhone · iPad · Android) | `/fridge-pick-support/` | App Store link live (`https://apps.apple.com/app/id6828103127`). Google Play: coming soon. |
| Jewelers Handbook (iPhone · iPad) | `/jewelers-handbook-support/` | App Store: coming soon. |
| Lightwhirl (Mac) | `https://lightwhirl.app/` (privacy and support on that host) | Mac App Store: coming soon. |

### Language

The site is English only. There is no `/ru/` tree, no language switcher, and no `hreflang` alternates. The build fails if a page contains Russian text or a leftover `/ru/` / `hreflang="ru"` link.

(Email support still offers a reply in English or Russian; that is stated on the support page and in the structured data, and is not a site-locale feature.)

### Security and privacy of the site itself

GitHub Pages cannot set HTTP headers, so each HTML page gets a meta Content-Security-Policy (inline scripts allowed only by their SHA-256 hash) and `referrer` set to `no-referrer`. The apps the site describes work offline and collect no personal data; this site does not host accounts, payments or user content.
