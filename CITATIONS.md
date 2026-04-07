# Citation System Documentation

A lightweight, web-optimized citation tool that processes your source metadata and generates formatted citations automatically.

## Quick Start

### 1. Add Your Sources
Edit `sources.yaml` to define your citations:

```yaml
sources:
  - id: "smith_2024"
    author: "John Smith"
    year: 2024
    title: "The Future of AI in Education"
    url: "https://example.com/article"
    type: "article"
    publisher: "Tech Press"
  
  - id: "doe_2023"
    author: "Jane Doe"
    year: 2023
    title: "Ethics in Machine Learning"
    url: "https://example.com/report"
    type: "report"
    publisher: "AI Institute"
```

**Fields:**
- `id` (required): Unique identifier — used to reference in markdown
- `author` (required): Author or organization name
- `year` (required): Publication year
- `title` (required): Work title
- `url` (required): Source URL or DOI
- `type` (required): One of: article, book, website, report, etc.
- `publisher` (optional): Publisher name
- `date_accessed` (optional): For web sources (YYYY-MM-DD format)

### 2. Use Citations in Your Content
In any markdown file, use this syntax to insert citations:

```
|src|'source_id'|'format'|
```

**Formats:**
- **Short**: `|src|'smith_2024'|'short'|` → renders as: "Smith (2024)"
- **Long**: `|src|'smith_2024'|'long'|` → renders as the full formatted citation

**Examples:**
```markdown
Recent research indicates |src|'smith_2024'|'short'| that AI is transforming education.

As detailed in |src|'smith_2024'|'long'|, the implications are far-reaching.
```

### 3. Generate Citations
Run the build script:

```bash
python build.py
```

The system will:
- Process all markdown files in `content/`
- Replace citation markers with formatted text
- Generate an alphabetically-sorted `citations.html` page
- Include the page in the built site

## How It Works

### Citation Processing Pipeline
1. **Parse markdown**: The build system reads all `.md` files
2. **Extract citations**: Finds all `|src|...|` markers
3. **Track usage**: Records which sources are referenced
4. **Replace markers**: Replaces markers with formatted text
5. **Generate bibliography**: Creates alphabeted citations page
6. **Build site**: Includes citations page in public site

### Citation Formats
The system generates:
- **Short format**: `Author (Year)` — ideal for inline mentions
- **Long format**: `Author (Year). Title. Publisher. URL` — full bibliographic entry

### Alphabetical Ordering
Citations appear in the bibliography sorted alphabetically by author last name (case-insensitive). The order you add them to your content doesn't matter — they'll be organized consistently on the citations page.

## Integration

### Linking to Citations Page
In your templates or content, link to the citations page:
```html
<a href="{{ base_url }}/citations.html">View all sources</a>
```

### Direct Citation Links
Each citation in the bibliography has an `id` attribute (format: `cite-{source_id}`), so you can deep-link:
```markdown
[See the full citation](citations.html#cite-smith_2024)
```

## API Reference

### CitationManager Class
Located in `citations.py`:

```python
from citations import CitationManager

# Initialize
manager = CitationManager("sources.yaml")

# Format a single citation
short = manager.format_short("smith_2024")  # Returns: "Smith (2024)"
long = manager.format_long("smith_2024")    # Returns: full formatted entry

# Process markdown content
processed, used = manager.process_content(markdown_text)
# Returns: (text_with_citations_replaced, list_of_source_ids_found)

# Generate complete bibliography
html = manager.generate_bibliography(["smith_2024", "doe_2023"])
# or generate all sources:
html = manager.generate_bibliography([])
```

## Tips & Tricks

### Source ID Naming
Use descriptive IDs that make sense to you:
- `lastname_year` ✓ (e.g., `smith_2024`)
- `topic-year` ✓ (e.g., `ai-ethics-2023`)
- Avoid spaces and special characters

### Multiple Authors
For multiple authors, list them as: `"Smith, J., Doe, J., & Brown, A."`

### Missing Information
If a field is missing:
- Short citations show: `[Citation not found: id]`
- Long citations attempt to format with available data

### Static Site Hosting
The generated `citations.html` is a standard HTML file and can be:
- Deployed to any static hosting (GitHub Pages, Netlify, etc.)
- Cached indefinitely (no dynamic generation)
- Embedded or linked from anywhere on your site

## Styling

Default styles are in `static/css/style.css` under "Bibliography / Citations". Customize by editing:
- `.bibliography` — container styles
- `.citation-entry` — source headings
- `dd` inside `.bibliography` — full entry text

## Troubleshooting

**Citation not appearing?**
- Check the source `id` matches exactly in `sources.yaml`
- Verify syntax: `|src|'id'|'short/long'|` with quotes
- Rebuild with `python build.py`

**Site won't build?**
- Ensure `sources.yaml` exists in project root
- Check YAML syntax (indentation matters!)
- Verify all required fields are present

**Want to exclude sources?**
- Remove them from `sources.yaml` — only referenced sources appear in bibliography
- Or manually edit the generated `citations.html` file

## Example Workflow

1. **Research phase**: Add sources to `sources.yaml` as you find them
2. **Writing phase**: Use `|src|'id'|'short'|` inline and `|src|'id'|'long'|` in detailed sections
3. **Review phase**: Run `python build.py` and check `_site/citations.html`
4. **Publish**: Deploy the built site — citations are automatically included and formatted
