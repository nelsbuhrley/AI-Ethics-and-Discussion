# AI in Education — Discussion Site

A static website for sharing perspectives on AI usage in education, hosted on **GitHub Pages** and built automatically with **GitHub Actions**.

---

## 🚀 How the site is built

A Python script (`build.py`) reads content files from the `content/` directory, runs them through Jinja2 HTML templates, and writes the finished HTML to `_site/`. GitHub Actions deploys `_site/` to GitHub Pages on every push to `main`.

---

## ✍️ Adding & editing content

### Main page

Edit **`content/index.md`**. Supports standard Markdown plus optional YAML front matter:

```yaml
---
title: My Page Title
subtitle: A short tagline shown in the hero
---

Your Markdown content here...
```

### Adding a new subpage

**Drop any `.md`, `.txt`, or `.docx` file into `content/pages/`.**

```
content/pages/my-new-topic.md   →  /pages/my-new-topic/
```

The file name becomes the URL slug. Add a `title:` and `description:` in the front matter and it will appear in the navigation and the card grid on the home page automatically.

```yaml
---
title: My New Topic
description: A one-sentence summary shown on the home page card.
---
```

### Adding a Q&A section to a page

Create a companion folder with a `qa/` subdirectory:

```
content/pages/my-new-topic/
└── qa/
    └── 01-questions.md
```

Each `.md` file in the `qa/` folder can contain one or more Q&A pairs:

```markdown
## Question goes here?

Full **Markdown** answer goes here. Can span multiple paragraphs.

## Another question?

Another answer.
```

Q&A for the **main page** lives in `content/qa/`.

### Internal links

Use double-bracket syntax anywhere in your Markdown:

```markdown
[[page-name]]                    links to /pages/page-name/
[[page-name|Custom Link Text]]   same, with custom anchor text
```

Where `page-name` matches the slug (filename without extension, lowercased, spaces → hyphens).

---

## 🛠 Local development

```bash
# Install dependencies (Python 3.9+)
pip install -r requirements.txt

# Build the site
python build.py

# Preview (macOS/Linux)
cd _site && python -m http.server 8000
```

Open `http://localhost:8000` in your browser.

---

## 📁 Repository structure

```
.github/workflows/deploy.yml   GitHub Actions build + deploy workflow
build.py                       Static site builder
requirements.txt               Python dependencies
templates/                     Jinja2 HTML templates
  base.html
  index.html
  page.html
static/
  css/style.css                Styles
  js/main.js                   Accordion + mobile nav
content/
  index.md                     Main page content
  qa/                          Q&A items for the main page
  pages/                       Subpages (drop files here)
    <topic>.md
    <topic>/qa/                Q&A items for that subpage
_site/                         Generated output (gitignored)
```
