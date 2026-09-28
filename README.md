# App support website

Static HTML and CSS for raisecheckfold.com. Published pages require no JavaScript or server-side runtime.

## Local preview

Run `python3 -m http.server 8000` from this directory, then open http://localhost:8000.

## Languages

The app directory and all pikPal, PokerNote, and DogKona support, beta, and privacy pages are available in English, French, Japanese, Traditional Chinese, Simplified Chinese, and Spanish. The language switcher opens the equivalent page, and internal navigation keeps the selected language. English uses the original paths; translated pages live in `fr/`, `ja/`, `zh-hant/`, `zh-hans/`, and `es/` under the relevant app directory. The translated app directories are at the site root, for example `fr/index.html`. Existing pikPal Traditional Chinese URLs are preserved.

Every page has a matching HTML language, canonical URL, and reciprocal `hreflang` links. Navigation works without JavaScript. Language selection is explicit; there are no automatic redirects or cookies.

### Editing content

1. Edit the English HTML layout/content in `locales/templates/` rather than the generated public pages.
2. Update the corresponding text in `locales/en.json` and all five translated catalogs. Numeric keys are stable translation IDs; append new IDs rather than renumbering existing entries. Names and email addresses intentionally remain unchanged. Keep inline text fragments consistent with their surrounding sentence.
3. Run `python3 scripts/build_locales.py` to regenerate the 48 public pages. This optional authoring command uses only the Python standard library. Generated pages are checked in, so hosting requires no build step.
4. Run the validation commands below and review layout in a browser.

The generator requires complete catalogs and rejects unknown source text. It translates visible text, document titles, descriptions, image alternatives, and accessible labels. Asset paths remain shared; local page links are rewritten for each language. The previously incomplete Traditional Chinese pikPal policy is now translated from the same English source as the other languages.

## Structure

- `index.html`: generated English app directory.
- `assets/css/base.css`: shared typography and keyboard/motion accessibility.
- `assets/css/home.css`: app directory layout.
- `assets/css/document.css`: shared support and privacy document layout.
- `assets/css/languages.css`: language navigation and translated heading layout.
- `assets/css/glass.css`: shared liquid-glass-inspired theme, with app palettes, opaque fallbacks, and reduced-transparency/motion support. Loaded last by the page generator.
- `locales/`: translation catalogs and source templates.
- `pikpalinfo/`, `pokerplayernote/`, `dogkona/`: generated public pages, shared app styles, and assets.
- `dogkona/index/`, `dogkona/privacy/`: existing compatibility redirects.

Keep relative links so previews work without the production domain. Existing public paths, `CNAME`, and advertising verification files are deployment inputs and should remain stable.

## Validation

```sh
python3 scripts/build_locales.py --check
python3 scripts/check_site.py
python3 scripts/test_locales.py
```

These commands verify reproducible output, local assets and fragment links, basic accessibility markup, catalog completeness, translated routing, escaped output, language switchers, and canonical/alternate metadata. Check layout and keyboard navigation in a browser after changing styles.

## Existing content limitations

The pikPal App Store buttons still have placeholder destinations. The external Android beta signup service and text inside app screenshots are outside this repository; their content is not translated by this site generator.

## pokerNote listing alignment

The pokerNote marketing and privacy pages were reconciled with the [App Store listing](https://apps.apple.com/us/app/pokernote/id6471785611) and Apple's live lookup response on September 28, 2026. The listing's four app languages are distinct from the website's six translations. Live release notes confirm CSV export and JSON backup/restore; do not infer released features solely from local development code. Screenshots and their source URLs are documented in `pokerplayernote/assets/SOURCES.md`. Privacy copy separates local records from advertising and attributes the published disclosure categories to the App Store listing.
