#!/usr/bin/env python3
"""
Static site builder for AI Ethics and Discussion website.

Content structure
─────────────────
  content/
  ├── index.md                 Main page body (supports YAML front matter)
  ├── qa/                      Q&A section for the main page
  │   ├── 01-question.md       Each file holds one or more Q&A pairs
  │   └── 02-question.md
  └── pages/                   Subpages — drop any .md/.txt/.docx here
      ├── some-topic.md        → /pages/some-topic/
      ├── some-topic/          Optional companion folder for the page above
      │   └── qa/              Q&A section appended to that subpage
      │       └── 01-qa.md
      └── another-topic/       Folder-based page (needs index.md inside)
          ├── index.md
          └── qa/
              └── 01-qa.md

Q&A file format
───────────────
  ## Question goes here?

  Full **markdown** answer goes here.

  ## Another question?

  Another answer.

Internal link syntax
────────────────────
  [[page-name]]                 → links to /pages/page-name/
  [[page-name|Custom Text]]     → same but with custom anchor text
  Standard Markdown links work as well.
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import markdown as md_lib
import yaml
from jinja2 import Environment, FileSystemLoader

from citations import CitationManager

try:
    import mammoth
    HAS_MAMMOTH = True
except ImportError:
    HAS_MAMMOTH = False

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONTENT_DIR  = Path("content")
TEMPLATES_DIR = Path("templates")
STATIC_DIR   = Path("static")
OUTPUT_DIR   = Path("_site")
SOURCES_FILE = Path("sources.yaml")

CONTENT_EXTENSIONS = {".md", ".markdown", ".txt", ".docx"}

# Detect base URL automatically from GITHUB_REPOSITORY env var.
# Project pages live at  https://<owner>.github.io/<repo>/
# User pages live at     https://<owner>.github.io/
_gh_repo = os.environ.get("GITHUB_REPOSITORY", "")
if _gh_repo:
    _owner, _repo = (_gh_repo.split("/", 1) + [""])[:2]
    BASE_URL = "" if _repo.lower() == f"{_owner.lower()}.github.io" else f"/{_repo}"
else:
    BASE_URL = os.environ.get("SITE_BASE_URL", "")

# Initialize citation manager
citation_manager = CitationManager(str(SOURCES_FILE))

# ---------------------------------------------------------------------------
# Markdown processor
# ---------------------------------------------------------------------------

_md = md_lib.Markdown(
    extensions=["extra", "toc", "tables", "fenced_code", "nl2br"],
    extension_configs={
        "toc": {"permalink": True},
    },
)

# Track all citations used in the entire site
_all_citations_used = set()


def _convert_markdown(text: str) -> str:
    _md.reset()
    return _md.convert(text)


def process_citations_in_markdown(text: str) -> str:
    """
    Process citation markers in text and replace with formatted citations.
    Also tracks all citations for the bibliography.
    """
    processed, used = citation_manager.process_content(text)
    _all_citations_used.update(used)
    return processed


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert any text to a URL-safe slug."""
    text = str(text).lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def parse_front_matter(raw: str):
    """Strip and parse YAML front matter; return (meta_dict, body_str)."""
    meta: dict = {}
    body = raw
    if raw.startswith("---"):
        try:
            end = raw.index("---", 3)
            meta = yaml.safe_load(raw[3:end].strip()) or {}
            body = raw[end + 3:].strip()
        except (ValueError, yaml.YAMLError):
            pass
    return meta, body


def process_internal_links(text: str) -> str:
    """
    Replace  [[page-name]]  and  [[page-name|Display Text]]
    with proper Markdown links pointing at /pages/<slug>/.
    """
    def _replace(m: re.Match) -> str:
        page  = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else page.replace("-", " ").title()
        return f"[{label}]({BASE_URL}/pages/{slugify(page)}/)"

    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", _replace, text)


def file_to_html(path: Path) -> tuple[dict, str]:
    """Convert a content file (.md / .txt / .docx) to (meta, html)."""
    ext = path.suffix.lower()

    if ext in {".md", ".markdown", ".txt"}:
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)
        body = process_internal_links(body)
        body = process_citations_in_markdown(body)  # Process citations
        return meta, _convert_markdown(body)

    if ext == ".docx" and HAS_MAMMOTH:
        with path.open("rb") as fh:
            result = mammoth.convert_to_html(fh)
        return {}, result.value

    return {}, f"<p><em>Unsupported file type: {ext}</em></p>"


def extract_title(meta: dict, html: str, fallback: str) -> str:
    """Return the best title we can find for a page."""
    if "title" in meta:
        return str(meta["title"])
    m = re.search(r"<h[12][^>]*>(.*?)</h[12]>", html, re.IGNORECASE)
    if m:
        return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return fallback


# ---------------------------------------------------------------------------
# Q&A loading
# ---------------------------------------------------------------------------

def load_qa_items(qa_dir: Path) -> list[dict]:
    """
    Load all Q&A pairs from *.md / *.txt files in *qa_dir*.

    Each file may contain one or more pairs in the format::

        ## Question text?

        Answer in **Markdown**.

        ## Another question?

        Another answer.
    """
    if not qa_dir.is_dir():
        return []

    items: list[dict] = []
    for fpath in sorted(qa_dir.iterdir()):
        if fpath.suffix.lower() not in {".md", ".markdown", ".txt"}:
            continue
        _, body = parse_front_matter(fpath.read_text(encoding="utf-8"))
        sections = re.split(r"^##\s+", body, flags=re.MULTILINE)
        for section in sections:
            section = section.strip()
            if not section:
                continue
            lines = section.split("\n", 1)
            question = lines[0].strip().rstrip("?") + "?"
            answer_md = lines[1].strip() if len(lines) > 1 else ""
            items.append({"question": question, "answer": _convert_markdown(answer_md)})

    return items


# ---------------------------------------------------------------------------
# Page discovery
# ---------------------------------------------------------------------------

def discover_pages(pages_dir: Path) -> list[dict]:
    """
    Walk *pages_dir* and return a list of page descriptor dicts.

    Each dict has:
      slug        URL slug
      title       Display title (from front matter or derived from filename)
      description Short description (from front matter, optional)
      source      Path to the content file
      qa_dir      Path to the companion qa/ folder (may not exist)
    """
    if not pages_dir.is_dir():
        return []

    pages: list[dict] = []
    seen: set[str] = set()

    def _add(source: Path, slug: str, qa_dir: Path) -> None:
        if slug in seen:
            return
        seen.add(slug)
        meta, html = file_to_html(source)
        stem = source.stem if source.name != "index.md" else source.parent.name
        title = extract_title(meta, html, stem.replace("-", " ").replace("_", " ").title())
        pages.append(
            {
                "slug": slug,
                "title": title,
                "description": meta.get("description", ""),
                "source": source,
                "qa_dir": qa_dir,
            }
        )

    for item in sorted(pages_dir.iterdir()):
        if item.is_file() and item.suffix.lower() in CONTENT_EXTENSIONS:
            slug = slugify(item.stem)
            qa_dir = pages_dir / item.stem / "qa"
            _add(item, slug, qa_dir)

        elif item.is_dir() and not item.name.startswith(".") and item.name != "qa":
            # Folder-based page — look for an index file
            index = next(
                (
                    item / fname
                    for fname in ("index.md", "index.txt", "README.md")
                    if (item / fname).exists()
                ),
                None,
            )
            if index:
                slug = slugify(item.name)
                _add(index, slug, item / "qa")

    return pages


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> None:
    # ── Clean / prepare output directory ──────────────────────────────────
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir()

    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, OUTPUT_DIR / "static")

    # ── Jinja2 environment ─────────────────────────────────────────────────
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)

    common_ctx = {
        "base_url": BASE_URL,
        "site_title": "AI in Education",
        "site_description": "Exploring AI's role in education — perspectives, ethics, and the future.",
        "current_year": datetime.now().year,
    }

    # ── Discover subpages (needed for nav in every template) ──────────────
    pages_info = discover_pages(CONTENT_DIR / "pages")

    nav_pages = [
        {"slug": p["slug"], "title": p["title"], "description": p["description"]}
        for p in pages_info
    ]

    # ── Main (index) page ─────────────────────────────────────────────────
    index_file = next(
        (
            CONTENT_DIR / f
            for f in ("index.md", "index.txt")
            if (CONTENT_DIR / f).exists()
        ),
        None,
    )

    main_meta: dict = {}
    main_html = "<p>Welcome to AI Ethics and Discussion.</p>"
    if index_file:
        main_meta, main_html = file_to_html(index_file)

    main_qa = load_qa_items(CONTENT_DIR / "qa")

    tmpl = env.get_template("index.html")
    rendered = tmpl.render(
        **common_ctx,
        page_title=main_meta.get("title", "AI in Education"),
        page_subtitle=main_meta.get("subtitle", ""),
        content=main_html,
        qa_items=main_qa,
        pages=nav_pages,
        is_home=True,
        current_slug=None,
    )
    (OUTPUT_DIR / "index.html").write_text(rendered, encoding="utf-8")
    print("  ✓  index.html")

    # ── Subpages ───────────────────────────────────────────────────────────
    if pages_info:
        pages_out = OUTPUT_DIR / "pages"
        pages_out.mkdir()

        for page in pages_info:
            _, html = file_to_html(page["source"])
            qa_items = load_qa_items(page["qa_dir"])
            page_dir = pages_out / page["slug"]
            page_dir.mkdir(exist_ok=True)

            tmpl = env.get_template("page.html")
            rendered = tmpl.render(
                **common_ctx,
                page_title=page["title"],
                content=html,
                qa_items=qa_items,
                pages=nav_pages,
                is_home=False,
                current_slug=page["slug"],
            )
            (page_dir / "index.html").write_text(rendered, encoding="utf-8")
            print(f"  ✓  pages/{page['slug']}/index.html")

    # ── Citations page ─────────────────────────────────────────────────────
    if _all_citations_used:
        citations_html = citation_manager.generate_bibliography(list(_all_citations_used))
        tmpl = env.get_template("citations.html")
        rendered = tmpl.render(
            **common_ctx,
            page_title="Sources",
            citations=citations_html,
            pages=nav_pages,
            is_home=False,
            current_slug="sources",
        )
        (OUTPUT_DIR / "citations.html").write_text(rendered, encoding="utf-8")
        print("  ✓  citations.html")

    print(f"\nSite built → {OUTPUT_DIR}/  (BASE_URL='{BASE_URL}')")


if __name__ == "__main__":
    build()
