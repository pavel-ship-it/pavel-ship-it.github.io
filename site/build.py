#!/usr/bin/env python3
"""Builds Pavel Yakimenko's developer site into ../docs (GitHub Pages user site, served from main:/docs
at https://pavel-ship-it.github.io/).

Same generator approach as the Fridge Pick and Jewelers Handbook sites. Edit site/ (templates/, content/,
assets/, config.json) and run:
    python3 site/build.py
Needs: jinja2  (pip install jinja2)

The site is in English. Canonical URLs have no .html suffix (/support);
GitHub Pages also serves /support.html. robots.txt here is the root robots.txt for the whole
pavel-ship-it.github.io host, so it also lists the two app sitemaps.
"""
import json, os, re, shutil, hashlib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, 'docs')
CFG = json.load(open(os.path.join(HERE, 'config.json'), encoding='utf-8'))
BASE_URL, BASE_PATH = CFG['base_url'], CFG['base_path']
NAME = 'Pavel Yakimenko'
EXTRA_SITEMAPS = ['/fridge-pick-support/sitemap.xml', '/jewelers-handbook-support/sitemap.xml']


def rel(u):
    return BASE_PATH + u


def abs_(u):
    return BASE_URL + BASE_PATH + u


def mailto(subject):
    return f"mailto:{CFG['email']}?subject={quote(subject)}"


T = dict(
    locale='en_US',
    skip='Skip to content', nav_label='Main', footer_nav='Site', crumbs_label='Breadcrumb',
    nav_home='Home', nav_apps='Apps', nav_support='Support', nav_privacy='Privacy',
    home='/', support='/support', privacy='/privacy',
    footer_tagline='Indie developer. Apps that work offline and collect no personal data.',
    footer_contact='Questions or ideas?', footer_apps='Apps',
    og_alt='Pavel Yakimenko, indie developer: Fridge Pick, Jewelers Handbook and Lightwhirl',
    soon_apple='Coming soon to the App Store', soon_play='Coming soon to Google Play',
    badge_soon='Coming soon to the', badge_apple_small='Download on the', badge_google_small='Get it on',
)

URLS = {'home': '/', 'support': '/support', 'privacy': '/privacy'}

PAGES = {
    'home': dict(title='Pavel Yakimenko – Indie Developer: Fridge Pick, Jewelers Handbook, Lightwhirl',
                 og_title='Pavel Yakimenko – Indie Developer',
                 description='Apps by Pavel Yakimenko: Fridge Pick, quick meal ideas from what’s in your fridge, and Jewelers Handbook, an offline reference and calculators for jewelers, and Lightwhirl, a music visualizer for Mac. Support and privacy in one place.'),
    'support': dict(title='Support – Apps by Pavel Yakimenko', crumb='Support',
                    description='Get help with Fridge Pick, Jewelers Handbook and Lightwhirl: email the developer, report a bug or suggest an idea, and find each app’s manual and privacy policy.'),
    'privacy': dict(title='Privacy Policies – Apps by Pavel Yakimenko', crumb='Privacy',
                    description='Privacy policies of Fridge Pick, Jewelers Handbook and Lightwhirl. None of the apps collects personal data, has accounts, ads or tracking.'),
}

# per-app texts (true facts taken from each app's own site)
APP_TXT = {
    'fridge-pick': dict(blurb='Quick meal ideas from what’s in your fridge. Tick the products you have and see what you can cook right now, get suggestions when you’re hungry, plan your week and keep a shopping list. Works offline, no account.',
                        subject='Fridge Pick support', include_os='iOS or Android version'),
    'lightwhirl': dict(blurb='A music visualizer for Mac. Play anything on your Mac and watch it turn into light: eight feedback presets and two photo scenes, Northern Sky and Fireplace, that move with the beat, fullscreen in one key. Nothing leaves your Mac.',
                       subject='Lightwhirl support', include_os='macOS version'),
    'jewelers-handbook': dict(blurb='An offline reference and calculator kit for jewelers: chain calculators with 3D models at actual size, gemstones, cuts, settings and clasps, carat estimate, ring sizes and metal weight. No account.',
                              subject='Jewelers Handbook support', include_os='iOS or iPadOS version'),
}


def ld(obj):
    return Markup(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))


def out_path(url):
    p = url.lstrip('/')
    if p == '' or p.endswith('/'):
        return os.path.join(OUT, p, 'index.html')
    return os.path.join(OUT, p + '.html')


def check_en(path, text):
    """English-only site: no Russian text and no leftover /ru/ links."""
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    bad = sorted(set(m.group(0) for m in re.finditer(r'\S*[\u0400-\u04FF]\S*', t)))
    if bad:
        raise SystemExit(f'Russian text on {path}: {bad[:10]}')
    if '/ru/' in text or re.search(r'hreflang="ru"', text):
        raise SystemExit(f'/ru/ or Russian hreflang leftover on {path}')


def apps_for():
    res = []
    for a in CFG['apps']:
        x = dict(a, **APP_TXT[a['id']])
        x['name_l'], x['short_l'] = a['name'], a['short']
        x['platforms_l'] = a['platforms']
        x['url'] = a['site']
        base = x['url']
        x['manual'], x['privacy'], x['support'] = base + 'manual/', base + 'privacy', base + 'support'
        if 'manual' in a:
            x['manual'] = a['manual']
        if 'privacy' in a:
            x['privacy'] = a['privacy']
        if 'support' in a:
            x['support'] = a['support']
        x['external'] = x['url'].startswith('http')
        x['mailto'] = mailto(x['subject'])
        res.append(x)
    return res


def graph(page):
    person = {'@type': 'Person', '@id': abs_('/#person'), 'name': NAME, 'url': abs_('/'),
              'jobTitle': 'Indie developer',
              'email': 'mailto:' + CFG['email'], 'image': abs_('/assets/img/mark-512.png'),
              'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': CFG['email'],
                               'url': abs_('/support'), 'availableLanguage': ['English', 'Russian']}}
    org = {'@type': 'Organization', '@id': abs_('/#developer'), 'name': NAME, 'url': abs_('/'),
           'logo': abs_('/assets/img/mark-512.png'), 'founder': {'@id': abs_('/#person')},
           'contactPoint': person['contactPoint']}
    site = {'@type': 'WebSite', '@id': abs_('/#website'), 'name': NAME, 'url': abs_('/'),
            'inLanguage': 'en', 'publisher': {'@id': abs_('/#developer')}}
    apps = []
    for a in apps_for():
        pre = '' if a['external'] else BASE_URL
        img = a['site'] + 'assets/img/icon-512.png' if a['external'] else BASE_URL + a['site'] + 'assets/img/icon-512.jpg'
        app = {'@type': 'SoftwareApplication', '@id': pre + a['site'] + '#app', 'name': a['name_l'],
               'url': pre + a['url'], 'operatingSystem': a['os'], 'applicationCategory': a['category'],
               'image': img, 'description': a['blurb'],
               'author': {'@id': abs_('/#person')}, 'publisher': {'@id': abs_('/#developer')}}
        same = [v for v in a['stores'].values() if v]
        if same:
            app['sameAs'] = same
        apps.append(app)
    org['owns'] = [{'@id': x['@id']} for x in apps]
    return {'@context': 'https://schema.org', '@graph': [person, org, site] + apps}


def main():
    env = Environment(loader=FileSystemLoader([os.path.join(HERE, 'templates'), os.path.join(HERE, 'content')]),
                      autoescape=select_autoescape(['html']))
    css = open(os.path.join(HERE, 'assets', 'site.css'), 'rb').read()
    env.globals.update(rel=rel, abs=abs_, css_version=hashlib.md5(css).hexdigest()[:8], email=CFG['email'],
                       mailto=mailto, base_url=BASE_URL)

    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(HERE, 'assets'), os.path.join(OUT, 'assets'))
    for f in ('favicon.ico', 'favicon.png', 'apple-touch-icon.png'):
        shutil.copy(os.path.join(HERE, f), OUT)
    open(os.path.join(OUT, '.nojekyll'), 'w').close()

    apps = apps_for()
    for key, meta in PAGES.items():
        url = URLS[key]
        page = dict(meta, url=url, kind=key, jsonld=[])
        if key == 'home':
            page['jsonld'].append(ld(graph(page)))
        else:
            page['crumbs'] = [(T['nav_home'], T['home']), (meta['crumb'], url)]
            page['jsonld'].append(ld({
                '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_(u)}
                                    for i, (n, u) in enumerate(page['crumbs'])]}))
        if key == 'support':
            page['jsonld'].append(ld({'@context': 'https://schema.org', '@type': 'ContactPage', 'url': abs_(url),
                                      'inLanguage': 'en', 'name': meta['title'],
                                      'about': {'@type': 'Person', '@id': abs_('/#person'), 'name': NAME,
                                                'email': 'mailto:' + CFG['email']}}))
        ctx = dict(lang='en', t=T, page=page, apps=apps)
        body = env.get_template(f'en/{key}.html').render(**ctx)
        html_out = env.get_template('base.html').render(body=Markup(body), **ctx)
        check_en(url, html_out)
        p = out_path(url)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, 'w', encoding='utf-8').write(html_out)

    page = dict(title='Page not found – Pavel Yakimenko', description='This page does not exist.',
                url='/404', kind='404', jsonld=[], robots='noindex')
    ctx = dict(lang='en', t=T, page=page, apps=apps)
    html404 = env.get_template('base.html').render(body=Markup(env.get_template('404.html').render(**ctx)), **ctx)
    check_en('404.html', html404)
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(html404)

    prio = {'home': '1.0', 'support': '0.9', 'privacy': '0.5'}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for key, u in URLS.items():
        lines += ['  <url>', f'    <loc>{abs_(u)}</loc>', f'    <lastmod>{CFG["lastmod"]}</lastmod>',
                  f'    <priority>{prio[key]}</priority>', '  </url>']
    lines.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('\n'.join(lines) + '\n')
    robots = 'User-agent: *\nAllow: /\n\n' + ''.join(f'Sitemap: {BASE_URL}{u}\n' for u in ['/sitemap.xml'] + EXTRA_SITEMAPS)
    open(os.path.join(OUT, 'robots.txt'), 'w').write(robots)
    print('built', len(URLS), 'pages + 404 into', OUT)


# --- Security: per-page meta CSP (GitHub Pages cannot set headers). Inline <script> blocks are allowed by
# their sha256 hash, so editing a script just needs a rebuild. JSON-LD data blocks are not executed and need no hash.
# frame-ancestors is not supported in <meta> CSP, so it is intentionally absent.
def add_csp(out_dir):
    import base64, glob as _glob, hashlib, re as _re
    for path in _glob.glob(os.path.join(out_dir, '**', '*.html'), recursive=True):
        s = open(path, encoding='utf-8').read()
        if 'http-equiv="Content-Security-Policy"' in s:
            continue
        hashes = sorted({"'sha256-" + base64.b64encode(hashlib.sha256(m.group(1).encode('utf-8')).digest()).decode() + "'"
                         for m in _re.finditer(r'<script>(.*?)</script>', s, _re.S)})
        csp = ("default-src 'none'; script-src 'self' " + ' '.join(hashes) + "; style-src 'self'; img-src 'self'; "
               "font-src 'self'; connect-src 'self'; manifest-src 'self'; base-uri 'none'; form-action 'none'; "
               "upgrade-insecure-requests")
        meta = ('\n<meta http-equiv="Content-Security-Policy" content="' + csp + '">'
                '\n<meta name="referrer" content="no-referrer">')
        assert '<meta charset="utf-8">' in s, path
        s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">' + meta, 1)
        open(path, 'w', encoding='utf-8').write(s)


if __name__ == '__main__':
    main()
    add_csp(OUT)
