"""Render every language as static HTML. Uses only the Python standard library."""
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import argparse
import json
import posixpath
import re

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {'en': 'English', 'fr': 'Français', 'ja': '日本語', 'zh-Hant': '繁體中文', 'zh-Hans': '简体中文', 'es': 'Español'}
LANG_LABELS = {'en': 'Language', 'fr': 'Langue', 'ja': '言語', 'zh-Hant': '語言', 'zh-Hans': '语言', 'es': 'Idioma'}
PAGES = ['index.html', 'pikpalinfo/index.html', 'pikpalinfo/android-beta.html', 'pikpalinfo/privacy-policy.html', 'pokerplayernote/index.html', 'pokerplayernote/privacy/index.html', 'dogkona/index.html', 'dogkona/privacy-policy.html']
ORIGIN = 'https://www.raisecheckfold.com/'


def localized(page, language):
    if language == 'en':
        return page
    parts = page.split('/')
    parts.insert(1 if len(parts) > 1 else 0, language.lower())
    return '/'.join(parts)


def relative(target, current):
    return posixpath.relpath(target, posixpath.dirname(current) or '.')


class Renderer(HTMLParser):
    def __init__(self, page, language, source, catalog):
        super().__init__(convert_charrefs=True)
        self.page, self.language = page, language
        self.current = localized(page, language)
        self.translations = {text: catalog[key] for key, text in source.items()}
        self.output = []
        self.used = set()

    def translate(self, text):
        normalized = ' '.join(text.split())
        if not normalized or not re.search(r'[A-Za-z]', normalized):
            return text
        if normalized not in self.translations:
            raise ValueError(f'{self.page}: text missing from catalog: {normalized}')
        self.used.add(normalized)
        leading = text[:len(text) - len(text.lstrip())]
        trailing = text[len(text.rstrip()):]
        return leading + self.translations[normalized] + trailing

    def rewrite_url(self, value):
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path:
            return value
        target = posixpath.normpath(posixpath.join(posixpath.dirname(self.page), url.path))
        if url.path.endswith('/'):
            target = posixpath.normpath(posixpath.join(target, 'index.html'))
        if target in PAGES:
            target = localized(target, self.language)
        return urlunsplit(('', '', relative(target, self.current), url.query, url.fragment))

    def switcher(self):
        links = []
        for code, label in LANGUAGES.items():
            active = ' aria-current="page"' if code == self.language else ''
            links.append(f'<a href="{relative(localized(self.page, code), self.current)}" lang="{code}" hreflang="{code}"{active}>{label}</a>')
        return f'<div class="language-switcher" role="navigation" aria-label="{LANG_LABELS[self.language]}">' + ''.join(links) + '</div>\n'

    def handle_decl(self, decl):
        self.output.append(f'<!{decl}>')

    def handle_comment(self, data):
        self.output.append(f'<!--{data}-->')

    def handle_data(self, data):
        self.output.append(escape(self.translate(data), quote=False))

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'link' and values.get('rel') == 'canonical':
            return
        if tag == 'main':
            self.output.append(self.switcher())
        updated = []
        for key, value in attrs:
            if tag == 'html' and key == 'lang':
                value = self.language
            elif key in ('href', 'src'):
                value = self.rewrite_url(value)
            elif key in ('alt', 'title', 'aria-label') or (tag == 'meta' and key == 'content' and values.get('name') == 'description'):
                value = self.translate(value) if value else value
            updated.append(key if value is None else f'{key}="{escape(value, quote=True)}"')
        self.output.append('<' + tag + (' ' + ' '.join(updated) if updated else '') + '>')

    def handle_endtag(self, tag):
        if tag == 'head':
            css = relative('assets/css/languages.css', self.current)
            self.output.append(f'<link rel="stylesheet" href="{css}">\n<link rel="canonical" href="{ORIGIN}{self.current}">\n')
            for code in LANGUAGES:
                self.output.append(f'<link rel="alternate" hreflang="{code}" href="{ORIGIN}{localized(self.page, code)}">\n')
            self.output.append(f'<link rel="alternate" hreflang="x-default" href="{ORIGIN}{self.page}">\n')
        self.output.append(f'</{tag}>')


def render(check=False):
    source = json.loads((ROOT / 'locales/en.json').read_text())
    failures = []
    count = 0
    for language in LANGUAGES:
        catalog = json.loads((ROOT / f'locales/{language.lower()}.json').read_text())
        if catalog.keys() != source.keys() or any(not isinstance(v, str) or not v for v in catalog.values()):
            raise ValueError(f'{language}: missing, extra, or empty translation entries')
        for page in PAGES:
            html = (ROOT / 'locales/templates' / page).read_text()
            html = re.sub(r'<div class="lang-switcher">.*?</div>', '', html, flags=re.S)
            html = re.sub(r'<a [^>]*class="language-link"[^>]*>.*?</a>', '', html, flags=re.S)
            renderer = Renderer(page, language, source, catalog)
            renderer.feed(html)
            result = '\n'.join(line.rstrip() for line in ''.join(renderer.output).splitlines()) + '\n'
            path = ROOT / localized(page, language)
            if check:
                if not path.exists() or path.read_text() != result:
                    failures.append(str(path.relative_to(ROOT)))
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(result)
            count += 1
    if failures:
        raise SystemExit('Generated pages need rebuilding: ' + ', '.join(failures))
    print(f'{"Verified" if check else "Generated"} {count} pages in {len(LANGUAGES)} languages.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    render(parser.parse_args().check)
