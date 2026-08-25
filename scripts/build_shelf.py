#!/usr/bin/env python3
"""Build the Knowledge Shelf homepage from data/books.json.

The catalog JSON is the single source of truth. This script renders
index.html through templates/index.template.html. With --check it
regenerates in memory and fails if the committed index.html is stale,
so the site can never drift from its data.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "books.json"
TEMPLATE = ROOT / "templates" / "index.template.html"
OUTPUT = ROOT / "index.html"
BOOKS_PER_SHELF = 4


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_books() -> list[dict]:
    books = json.loads(CATALOG.read_text(encoding="utf-8"))
    for i, book in enumerate(books):
        missing = [k for k in ("id", "title", "short_title", "href", "cover", "category", "summary", "accent", "published_at") if k not in book]
        if missing:
            raise SystemExit(f"books.json entry #{i} missing fields: {missing}")
    return sorted(books, key=lambda b: (b["published_at"], b["title"]), reverse=True)


def render_card(book: dict) -> str:
    searchable = " ".join((book["title"], book["short_title"], book["category"], book["summary"]))
    published = datetime.fromisoformat(book["published_at"]).strftime("%d/%m/%Y")
    return f"""      <article class="book-card" data-category="{esc(book['category'])}" data-search="{esc(searchable.lower())}" style="--accent:{esc(book['accent'])}">
        <a class="book-link" href="{esc(book['href'])}" aria-label="เปิดอ่าน {esc(book['title'])}">
          <div class="cover-wrap">
            <img class="cover" src="{esc(book['cover'])}" alt="ปก: {esc(book['short_title'])}" width="600" height="900" loading="lazy">
          </div>
          <div class="book-meta">
            <span class="category-pill">{esc(book['category'])}</span>
            <h3 class="book-title">{esc(book['short_title'])}</h3>
            <time class="publish-date" datetime="{esc(book['published_at'])}">publish on {published}</time>
            <p class="book-summary">{esc(book['summary'])}</p>
            <span class="read-cta">เปิดอ่าน →</span>
          </div>
        </a>
      </article>"""


def render_shelves(books: list[dict]) -> str:
    blocks: list[str] = []
    for start in range(0, len(books), BOOKS_PER_SHELF):
        shelf_books = books[start:start + BOOKS_PER_SHELF]
        cards = "\n".join(render_card(b) for b in shelf_books)
        blocks.append(f"""    <section class="shelf">
      <div class="shelf-row">
{cards}
      </div>
      <div class="shelf-board" aria-hidden="true"></div>
    </section>""")
    return "\n\n".join(blocks)


def render_page() -> str:
    books = load_books()
    template = TEMPLATE.read_text(encoding="utf-8")
    page = template.replace("{{BOOK_COUNT}}", str(len(books)))
    page = page.replace("{{SHELVES}}", render_shelves(books))
    page = page.replace("{{BUILD_STAMP}}", datetime.now().strftime("%Y-%m-%d %H:%M"))
    return page


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify index.html matches the catalog without writing")
    args = parser.parse_args()

    rendered = render_page()
    if args.check:
        if not OUTPUT.exists():
            print(f"CHECK FAIL: {OUTPUT} missing — run without --check first")
            return 1
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            print(f"CHECK FAIL: {OUTPUT} is stale vs data/books.json — rebuild needed")
            return 1
        print(f"CHECK OK: index.html in sync with {len(load_books())} books")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT} with {len(load_books())} books")
    return 0


if __name__ == "__main__":
    sys.exit(main())
