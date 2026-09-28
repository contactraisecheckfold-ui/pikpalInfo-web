# App support website

Static HTML and CSS for raisecheckfold.com. No build step or JavaScript framework is required.

## Local preview

Run `python3 -m http.server 8000` from this directory, then open http://localhost:8000.

## Structure

- `index.html`: app directory.
- `assets/css/base.css`: shared typography and keyboard/motion accessibility.
- `assets/css/home.css`: app directory layout.
- `assets/css/document.css`: shared support and privacy document layout.
- `pikpalinfo/`: English pages, Traditional Chinese pages in `zh-hant/`, and a shared app stylesheet.
- `pokerplayernote/`: support and privacy pages.
- `dogkona/`: independently themed app pages and compatibility redirects.

Keep relative links so previews work without the production domain. Existing public paths, `CNAME`, and advertising verification files are deployment inputs and should remain stable. Pages are plain HTML so navigation and content work without JavaScript.

## Validation

Run `python3 scripts/check_site.py` to check local destinations, fragment links, duplicate IDs, main landmarks, image alternatives, and iframe titles. Placeholder links are reported separately. Check layout and keyboard navigation in a browser after changing styles.

## Existing content to complete

The pikPal App Store buttons still have placeholder destinations. PokerNote's privacy policy and the Traditional Chinese pikPal privacy policy contain existing developer/date/contact placeholders. Confirm those details before replacing them; the refactor preserves policy wording.
