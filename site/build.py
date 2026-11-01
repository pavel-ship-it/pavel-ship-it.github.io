#!/usr/bin/env python3
"""Builds Pavel Yakimenko's developer site into ../docs (GitHub Pages user site, served from main:/docs
at https://pavel-ship-it.github.io/).

Same generator approach as the Fridge Pick and Jewelers Handbook sites. Edit site/ (templates/, content/,
assets/, config.json) and run:
    python3 site/build.py
Needs: jinja2  (pip install jinja2)

English at the root, Russian under /ru/. Canonical URLs have no .html suffix (/support);
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
CYR = re.compile('[\u0400-\u04FF]')
NAME = 'Pavel Yakimenko'
EXTRA_SITEMAPS = ['/fridge-pick-support/sitemap.xml', '/jewelers-handbook-support/sitemap.xml']


def rel(u):
    return BASE_PATH + u


def abs_(u):
    return BASE_URL + BASE_PATH + u


def mailto(subject):
    return f"mailto:{CFG['email']}?subject={quote(subject)}"


T = {
    'en': dict(
        locale='en_US', locale_alt='ru_RU', other='ru', other_label='Русский',
        skip='Skip to content', nav_label='Main', footer_nav='Site', crumbs_label='Breadcrumb',
        nav_home='Home', nav_apps='Apps', nav_support='Support', nav_privacy='Privacy',
        home='/', support='/support', privacy='/privacy',
        footer_tagline='Indie developer. Apps that work offline and collect no personal data.',
        footer_contact='Questions or ideas?', footer_apps='Apps',
        og_alt='Pavel Yakimenko, indie developer: Fridge Pick and Jewelers Handbook',
        soon_apple='Coming soon to the App Store', soon_play='Coming soon to Google Play',
        badge_soon='Coming soon to the', badge_apple_small='Download on the', badge_google_small='Get it on',
    ),
    'ru': dict(
        locale='ru_RU', locale_alt='en_US', other='en', other_label='English',
        skip='Перейти к содержанию', nav_label='Основное меню', footer_nav='Разделы сайта', crumbs_label='Навигационная цепочка',
        nav_home='Главная', nav_apps='Приложения', nav_support='Поддержка', nav_privacy='Конфиденциальность',
        home='/ru/', support='/ru/support', privacy='/ru/privacy',
        footer_tagline='Инди-разработчик. Приложения работают без интернета и не собирают персональные данные.',
        footer_contact='Вопросы или идеи?', footer_apps='Приложения',
        og_alt='Pavel Yakimenko, инди-разработчик: Fridge Pick и «Справочник ювелира»',
        soon_apple='Скоро в App Store', soon_play='Скоро в Google Play',
        badge_soon='Скоро в', badge_apple_small='Загрузите в', badge_google_small='Доступно в',
    ),
}

URLS = {'home': ('/', '/ru/'), 'support': ('/support', '/ru/support'), 'privacy': ('/privacy', '/ru/privacy')}

PAGES = {
    'en': {
        'home': dict(title='Pavel Yakimenko – Indie Developer: Fridge Pick and Jewelers Handbook',
                     og_title='Pavel Yakimenko – Indie Developer',
                     description='Apps by Pavel Yakimenko: Fridge Pick, quick meal ideas from what’s in your fridge, and Jewelers Handbook, an offline reference and calculators for jewelers. Support and privacy in one place.'),
        'support': dict(title='Support – Apps by Pavel Yakimenko', crumb='Support',
                        description='Get help with Fridge Pick and Jewelers Handbook: email the developer, report a bug or suggest an idea, and find each app’s manual and privacy policy.'),
        'privacy': dict(title='Privacy Policies – Apps by Pavel Yakimenko', crumb='Privacy',
                        description='Privacy policies of Fridge Pick and Jewelers Handbook. Neither app collects personal data, has accounts, ads or tracking.'),
    },
    'ru': {
        'home': dict(title='Pavel Yakimenko — инди-разработчик: Fridge Pick и «Справочник ювелира»',
                     og_title='Pavel Yakimenko — инди-разработчик',
                     description='Приложения Pavel Yakimenko: Fridge Pick — быстрые блюда из того, что есть в холодильнике, и «Справочник ювелира» — офлайн-справочник и калькуляторы для ювелира. Поддержка и конфиденциальность в одном месте.'),
        'support': dict(title='Поддержка – приложения Pavel Yakimenko', crumb='Поддержка',
                        description='Помощь по Fridge Pick и «Справочнику ювелира»: написать разработчику, сообщить об ошибке или предложить идею, руководства и политики конфиденциальности приложений.'),
        'privacy': dict(title='Политики конфиденциальности – приложения Pavel Yakimenko', crumb='Конфиденциальность',
                        description='Политики конфиденциальности Fridge Pick и «Справочника ювелира». Приложения не собирают персональные данные, в них нет учётных записей, рекламы и отслеживания.'),
    },
}

# per-app texts (true facts taken from each app's own site)
APP_TXT = {
    'fridge-pick': {
        'en': dict(blurb='Quick meal ideas from what’s in your fridge. Tick the products you have and see what you can cook right now, get suggestions when you’re hungry, plan your week and keep a shopping list. Works offline, no account.',
                   subject='Fridge Pick support', include_os='iOS or Android version'),
        'ru': dict(blurb='Быстрые блюда из того, что есть в холодильнике. Отметьте продукты и посмотрите, что можно приготовить прямо сейчас, получите идеи, когда хочется есть, спланируйте неделю и ведите список покупок. Без интернета и регистрации. Интерфейс пока на английском.',
                   subject='Fridge Pick: поддержка', include_os='версию iOS или Android'),
    },
    'jewelers-handbook': {
        'en': dict(blurb='An offline reference and calculator kit for jewelers: chain calculators with 3D models at actual size, gemstones, cuts, settings and clasps, carat estimate, ring sizes and metal weight. No account.',
                   subject='Jewelers Handbook support', include_os='iOS or iPadOS version'),
        'ru': dict(blurb='Офлайн-справочник и набор калькуляторов для ювелира: калькуляторы цепей с 3D-моделью в реальном размере, камни, огранки, закрепки и замки, оценка карат, размеры колец и вес металла. Без регистрации.',
                   subject='Справочник ювелира: поддержка', include_os='версию iOS или iPadOS'),
    },
}


def ld(obj):
    return Markup(json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/'))


def out_path(url):
    p = url.lstrip('/')
    if p == '' or p.endswith('/'):
        return os.path.join(OUT, p, 'index.html')
    return os.path.join(OUT, p + '.html')


def check_en(path, text):
    """English pages may contain Russian only in the language switcher label (and in JSON-LD alternateName)."""
    t = re.sub(r'<script type="application/ld\+json">.*?</script>', '', text, flags=re.S)
    t = t.replace('>Русский<', '><')
    bad = sorted(set(m.group(0) for m in re.finditer(r'\S*[\u0400-\u04FF]\S*', t)))
    if bad:
        raise SystemExit(f'Russian text on an English page {path}: {bad[:10]}')


def apps_for(lang):
    res = []
    for a in CFG['apps']:
        x = dict(a, **APP_TXT[a['id']][lang])
        x['name_l'], x['short_l'] = a['name'][lang], a['short'][lang]
        x['platforms_l'] = a['platforms'][lang]
        x['url'] = a['site'] if lang == 'en' else a['site_ru']
        base = x['url']
        x['manual'], x['privacy'], x['support'] = base + 'manual/', base + 'privacy', base + 'support'
        x['mailto'] = mailto(x['subject'])
        res.append(x)
    return res


def graph(lang, page):
    person = {'@type': 'Person', '@id': abs_('/#person'), 'name': NAME, 'url': abs_('/'),
              'jobTitle': 'Indie developer' if lang == 'en' else 'Инди-разработчик',
              'email': 'mailto:' + CFG['email'], 'image': abs_('/assets/img/mark-512.png'),
              'contactPoint': {'@type': 'ContactPoint', 'contactType': 'customer support', 'email': CFG['email'],
                               'url': abs_('/support'), 'availableLanguage': ['English', 'Russian']}}
    org = {'@type': 'Organization', '@id': abs_('/#developer'), 'name': NAME, 'url': abs_('/'),
           'logo': abs_('/assets/img/mark-512.png'), 'founder': {'@id': abs_('/#person')},
           'contactPoint': person['contactPoint']}
    site = {'@type': 'WebSite', '@id': abs_('/#website'), 'name': NAME, 'url': abs_('/'),
            'inLanguage': ['en', 'ru'], 'publisher': {'@id': abs_('/#developer')}}
    apps = []
    for a in apps_for(lang):
        app = {'@type': 'SoftwareApplication', '@id': BASE_URL + a['site'] + '#app', 'name': a['name_l'],
               'url': BASE_URL + a['url'], 'operatingSystem': a['os'], 'applicationCategory': a['category'],
               'image': BASE_URL + a['site'] + 'assets/img/icon-512.jpg', 'description': a['blurb'],
               'author': {'@id': abs_('/#person')}, 'publisher': {'@id': abs_('/#developer')}}
        if a['name']['ru'] != a['name']['en']:
            app['alternateName'] = a['name']['ru' if lang == 'en' else 'en']
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

    for lang in ('en', 'ru'):
        t = T[lang]
        for key, meta in PAGES[lang].items():
            url = URLS[key][0 if lang == 'en' else 1]
            page = dict(meta, url=url, kind=key, alternates={'en': URLS[key][0], 'ru': URLS[key][1]}, jsonld=[])
            if key == 'home':
                page['jsonld'].append(ld(graph(lang, page)))
            else:
                page['crumbs'] = [(t['nav_home'], t['home']), (meta['crumb'], url)]
                page['jsonld'].append(ld({
                    '@context': 'https://schema.org', '@type': 'BreadcrumbList',
                    'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': abs_(u)}
                                        for i, (n, u) in enumerate(page['crumbs'])]}))
            if key == 'support':
                page['jsonld'].append(ld({'@context': 'https://schema.org', '@type': 'ContactPage', 'url': abs_(url),
                                          'inLanguage': lang, 'name': meta['title'],
                                          'about': {'@type': 'Person', '@id': abs_('/#person'), 'name': NAME,
                                                    'email': 'mailto:' + CFG['email']}}))
            ctx = dict(lang=lang, t=t, page=page, apps=apps_for(lang))
            body = env.get_template(f'{lang}/{key}.html').render(**ctx)
            html_out = env.get_template('base.html').render(body=Markup(body), **ctx)
            p = out_path(url)
            if lang == 'en':
                check_en(p, html_out)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(html_out)

    page = dict(title='Page not found – Pavel Yakimenko', description='This page does not exist.',
                url='/404', kind='404', alternates={'en': '/', 'ru': '/ru/'}, jsonld=[], robots='noindex')
    ctx = dict(lang='en', t=T['en'], page=page, apps=apps_for('en'))
    html404 = env.get_template('base.html').render(body=Markup(env.get_template('404.html').render(**ctx)), **ctx)
    check_en('404.html', html404)
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(html404)

    prio = {'home': '1.0', 'support': '0.9', 'privacy': '0.5'}
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for key, (en, ru) in URLS.items():
        for u in (en, ru):
            lines += ['  <url>', f'    <loc>{abs_(u)}</loc>', f'    <lastmod>{CFG["lastmod"]}</lastmod>',
                      f'    <priority>{prio[key]}</priority>',
                      f'    <xhtml:link rel="alternate" hreflang="en" href="{abs_(en)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="ru" href="{abs_(ru)}"/>',
                      f'    <xhtml:link rel="alternate" hreflang="x-default" href="{abs_(en)}"/>', '  </url>']
    lines.append('</urlset>')
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write('\n'.join(lines) + '\n')
    robots = 'User-agent: *\nAllow: /\n\n' + ''.join(f'Sitemap: {BASE_URL}{u}\n' for u in ['/sitemap.xml'] + EXTRA_SITEMAPS)
    open(os.path.join(OUT, 'robots.txt'), 'w').write(robots)
    print('built', len(URLS) * 2, 'pages + 404 into', OUT)


if __name__ == '__main__':
    main()
