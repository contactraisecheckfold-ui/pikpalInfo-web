"""Check local links, assets, fragment targets, and basic page accessibility."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.ids = []
        self.refs = []
        self.errors = []
        self.mains = 0
        self.redirect = False
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('href', 'src'):
            if attrs.get(key):
                self.refs.append(attrs[key])
        self.mains += tag == 'main'
        if tag == 'meta' and attrs.get('http-equiv', '').lower() == 'refresh':
            self.redirect = True
        if tag == 'img' and 'alt' not in attrs:
            self.errors.append('Image missing alt text')
        if tag == 'iframe' and not attrs.get('title'):
            self.errors.append('Iframe missing title')


def main():
    pages = {path: Page(path) for path in ROOT.rglob('*.html') if '.git' not in path.parts}
    errors = []
    placeholders = []
    for path, page in pages.items():
        name = path.relative_to(ROOT)
        errors.extend(f'{name}: {error}' for error in page.errors)
        if not page.redirect and page.mains != 1:
            errors.append(f'{name}: expected one main landmark, found {page.mains}')
        for identifier, count in Counter(page.ids).items():
            if count > 1:
                errors.append(f'{name}: duplicate id {identifier}')
        for ref in page.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            if ref == '#':
                placeholders.append(f'{name}: placeholder link (#)')
                continue
            target = ((ROOT if url.path.startswith('/') else path.parent) / unquote(url.path.lstrip('/'))).resolve() if url.path else path
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{name}: missing local target {ref}')
            elif url.fragment and target in pages and unquote(url.fragment) not in pages[target].ids:
                errors.append(f'{name}: missing fragment {ref}')
    for message in errors:
        print(f'ERROR: {message}')
    for message in placeholders:
        print(f'NOTE: {message}')
    print(f'Checked {len(pages)} pages: {len(errors)} errors, {len(placeholders)} placeholder links.')
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
