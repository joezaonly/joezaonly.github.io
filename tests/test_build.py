#!/usr/bin/env python3
"""Tests for the Knowledge Shelf build pipeline."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_shelf  # noqa: E402


class CatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.books = build_shelf.load_books()

    def test_catalog_not_empty(self) -> None:
        self.assertGreater(len(self.books), 0)

    def test_ids_unique(self) -> None:
        ids = [b["id"] for b in self.books]
        self.assertEqual(len(ids), len(set(ids)))

    def test_book_pages_exist(self) -> None:
        for book in self.books:
            target = ROOT / book["href"]
            self.assertTrue(target.exists(), f"missing page: {book['href']}")

    def test_covers_exist(self) -> None:
        for book in self.books:
            target = ROOT / book["cover"]
            self.assertTrue(target.exists(), f"missing cover: {book['cover']}")

    def test_published_at_parseable(self) -> None:
        from datetime import datetime
        for book in self.books:
            datetime.fromisoformat(book["published_at"])

    def test_html_output_matches_template_placeholders(self) -> None:
        rendered = build_shelf.render_page()
        self.assertNotIn("{{BOOK_COUNT}}", rendered)
        self.assertNotIn("{{SHELVES}}", rendered)
        for book in self.books:
            self.assertIn(book["id"], rendered)


class CliTests(unittest.TestCase):
    def test_check_mode_succeeds_after_build(self) -> None:
        build = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_shelf.py")],
            capture_output=True, text=True,
        )
        self.assertEqual(build.returncode, 0, build.stderr)
        check = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_shelf.py"), "--check"],
            capture_output=True, text=True,
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)


if __name__ == "__main__":
    unittest.main()
