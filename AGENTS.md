# Project Agent Instructions — ชั้นหนังสือแห่งความรู้

This repository powers a personal knowledge library at GitHub Pages.

## Layout & sources of truth

- Reading catalog: `data/books.json` (single source of truth — never duplicate book facts elsewhere)
- Book pages: `books/<id>.html`
- Homepage generator: `scripts/build_shelf.py` (renders `index.html` from `templates/index.template.html`)
- Cover generator: `scripts/build_covers.py` (renders `assets/covers/<id>.png`, deterministic)
- Styles: `assets/css/`

## Workflow for adding a book

1. Append an entry to `data/books.json` (required fields: id, title, short_title, href, cover, category, summary, accent, published_at)
2. Write `books/<id>.html` using `assets/css/book.css`
3. Run `python3 scripts/build_covers.py` and `python3 scripts/build_shelf.py`
4. Run `python3 scripts/build_shelf.py --check` and `python3 -m unittest discover -s tests -v`
5. Commit locally. **Do not push publicly without explicit owner approval.**

## Authority rules

The assistant may edit the working tree, run generators/tests, preview locally, and prepare a scoped commit.
The assistant must obtain explicit approval before: public push, deleting books, changing this file, or adding secrets of any kind to the repo.

## Privacy

This repo is intended to become world-readable. Never commit: tokens, cookies, browser profiles, local absolute paths, signed/expiring media URLs, or private credentials.
