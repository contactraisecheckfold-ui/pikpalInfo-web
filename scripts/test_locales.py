"""Regression checks for static localization and language-preserving links."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import unittest

from build_locales import ROOT, PAGES, LANGUAGES, ORIGIN, Renderer, localized


class Tags(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.tags = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class LocalizationTests(unittest.TestCase):
    def test_catalog_coverage(self):
        source = json.loads((ROOT / 'locales/en.json').read_text())
        for language in LANGUAGES:
            catalog = json.loads((ROOT / f'locales/{language.lower()}.json').read_text())
            self.assertEqual(source.keys(), catalog.keys(), language)
            self.assertTrue(all(isinstance(value, str) and value for value in catalog.values()))

    def test_language_routes(self):
        renderer = Renderer('pokerplayernote/privacy/index.html', 'fr', {}, {})
        self.assertEqual(renderer.rewrite_url('../../'), '../../../fr/index.html')
        renderer = Renderer('pikpalinfo/index.html', 'ja', {}, {})
        self.assertEqual(renderer.rewrite_url('privacy-policy.html'), 'privacy-policy.html')
        self.assertEqual(renderer.rewrite_url('../index.html'), '../../ja/index.html')
        self.assertEqual(renderer.rewrite_url('index.html#faq'), 'index.html#faq')
        self.assertEqual(renderer.rewrite_url('app_mockup.png'), '../app_mockup.png')
        for url in ['#faq', '#', 'mailto:contactraisecheckfold@gmail.com', 'https://example.com/form?x=1']:
            self.assertEqual(renderer.rewrite_url(url), url)

    def test_untranslated_text_fails(self):
        renderer = Renderer('index.html', 'fr', {}, {})
        with self.assertRaisesRegex(ValueError, 'missing from catalog'):
            renderer.feed('<p>New content</p>')

    def test_translation_is_escaped(self):
        renderer = Renderer('index.html', 'fr', {'0': 'Example'}, {'0': '<script>alert(1)</script>'})
        renderer.feed('<p>Example</p>')
        self.assertEqual(''.join(renderer.output), '<p>&lt;script&gt;alert(1)&lt;/script&gt;</p>')

    def test_pokernote_store_links_and_screenshots(self):
        for language in LANGUAGES:
            page = ROOT / localized('pokerplayernote/index.html', language)
            tags = Tags(page.read_text()).tags
            store_buttons = [a for t, a in tags if t == 'a' and a.get('class') == 'button primary' and a.get('href') == 'https://apps.apple.com/us/app/pokernote/id6471785611']
            self.assertEqual(len(store_buttons), 1, language)
            screenshots = [a for t, a in tags if t == 'img' and any(a.get('src', '').endswith('/' + name + '.png') for name in ['table', 'players', 'tools'])]
            self.assertEqual(len(screenshots), 4, language)
            for screenshot in screenshots:
                self.assertTrue((page.parent / screenshot['src']).is_file())
                self.assertTrue(screenshot.get('alt'))
            policy = (ROOT / localized('pokerplayernote/privacy/index.html', language)).read_text()
            self.assertIn('id6471785611#app-privacy', policy)
            self.assertIn('https://policies.google.com/privacy', policy)
            self.assertNotIn('[Date]', policy)
            self.assertNotIn('[Your Company/Developer Name]', policy)

    def test_generated_metadata_and_switchers(self):
        for language in LANGUAGES:
            for page in PAGES:
                with self.subTest(language=language, page=page):
                    current = ROOT / localized(page, language)
                    tags = Tags(current.read_text()).tags
                    self.assertIn(('html', {'lang': language}), tags)
                    canonical = [a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'canonical']
                    self.assertEqual(canonical, [ORIGIN + localized(page, language)])
                    alternate = {a['hreflang']: a['href'] for t, a in tags if t == 'link' and a.get('rel') == 'alternate'}
                    self.assertEqual(set(alternate), set(LANGUAGES) | {'x-default'})
                    self.assertEqual(alternate['x-default'], ORIGIN + page)
                    switches = [a for t, a in tags if t == 'a' and 'hreflang' in a]
                    self.assertEqual(len(switches), len(LANGUAGES))
                    self.assertEqual([a['hreflang'] for a in switches if a.get('aria-current') == 'page'], [language])
                    for link in switches:
                        target = (current.parent / link['href']).resolve()
                        self.assertEqual(target, ROOT / localized(page, link['hreflang']))
                    # Every internal page link stays in the current language, except the switcher.
                    all_pages = {ROOT / localized(p, lang) for p in PAGES for lang in LANGUAGES}
                    same_language = {ROOT / localized(p, language) for p in PAGES}
                    for tag, attrs in tags:
                        if tag != 'a' or 'hreflang' in attrs or not attrs.get('href'):
                            continue
                        url = urlsplit(attrs['href'])
                        if url.scheme or url.netloc or not url.path:
                            continue
                        target = (current.parent / url.path).resolve()
                        if target in all_pages:
                            self.assertIn(target, same_language)


if __name__ == '__main__':
    unittest.main()
