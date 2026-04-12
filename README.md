# Stapler

A simple static site generator built with Jinja and Markdown.

## Installation

Clone the repo:

```bash
git clone https://github.com/gijs6/stapler.git
cd stapler
```

Create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

Install:

```bash
pip install -e .
```

Or with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Quick start

1. Create a `stapler.toml` in your project root:

```toml
[site]
url = "https://yoursite.com"
title = "Your site"
```

2. Put your content in a `site/` directory (the default). Templates go in `site/templates/`.

3. Run:

```bash
stapler serve   # local dev server on port 8000
stapler build   # production build
```

## Configuration

### Required

```toml
[site]
url = "https://yoursite.com"
title = "Your site"
```

### Optional

#### Site metadata

```toml
[site]
description = "About your site"
base_path = "/blog"                # Deploy to example.com/blog instead of the root
```

#### Author info

Used in RSS/Atom feeds.

```toml
[site.author]
name = "Your name"
email = "you@example.com"
```

#### Directories

All paths are relative to where you run `stapler`.

```toml
[directories]
site = "site"                      # Content directory (default: "site")
build = "build"                    # Production output (default: "build")
build_dev = "build-dev"            # Dev server output (default: "build-dev")
templates = "templates"            # Templates folder inside the site directory (default: "templates")
blog = "blog"                      # Blog posts folder inside the site directory (default: "blog")
```

#### Default template

The template used for HTML pages that have front matter but no `template` field.

```toml
[templates]
default = "base.html"
```

#### Blog

```toml
[features.blog]
enabled = true                     # Enable blog functionality (default: false)
template = "blog_post.html"        # Template for individual posts
index_template = "blog_index.html" # Template for the blog index page
```

#### Sitemap and feeds

```toml
[features]
sitemap = true                     # Generate sitemap.xml (default: true)

[features.feeds]
rss = true                         # Generate rss.xml (default: true)
atom = true                        # Generate atom.xml (default: true)
```

Feeds are only generated when the blog feature is enabled.

#### Markdown extensions

```toml
[markdown]
extensions = ["meta", "tables", "fenced_code"]  # Python-Markdown extensions
```

## How it works

### Pages

Any `.html` or `.md` file in your site directory (excluding the templates and blog folders) becomes a page.

#### Markdown files

Markdown files are always rendered to HTML. If the front matter includes a `template` field, the result is passed to that template as `page.content`. Without a `template` field (or without front matter entirely), the raw HTML is written directly.

```markdown
---
template: base.html
title: My page
---

# Content

Regular markdown here
```

#### HTML files

HTML files with front matter are rendered through a template. The `template` field in front matter takes precedence; if omitted, the default template from `[templates].default` is used.

```html
---
title: My page
---
<h1>Content here</h1>
```

HTML files without front matter are treated as Jinja templates directly:

```html
{% extends "base.html" %}
{% block content %}
<h1>Hello</h1>
{% endblock %}
```

Front matter is YAML. All fields are available as `page.metadata.<field>` in your templates.

#### Static files

Anything that's not a `.html` or `.md` file (and not in your templates or blog folder) is copied as-is to the output directory.

### Blog

Enable the blog feature in your config, then put `.md` files in your blog directory.

```markdown
---
title: My post
date: 2025-01-15
---

Post content here
```

The `date` field is optional. If omitted, stapler tries to infer it from the file's git history.

### Templates

Templates live in the directory you configured (default: `site/templates/`).

#### Available in all templates

- `data`: build info
  - `data.now`
    - `data.now.date.long`: build date as `%B %d, %Y` (e.g. `April 12, 2026`)
    - `data.now.date.short`: build date as `%Y-%m-%d` (e.g. `2026-04-12`)
    - `data.now.time`: build time as `%H:%M:%S`
    - `data.now.iso`: build datetime as ISO 8601
  - `data.last_commit`: last git commit info (`None` if not in a git repo)
    - `data.last_commit.hash.short`: short 7-character commit hash
    - `data.last_commit.hash.long`: full commit hash
    - `data.last_commit.dt.date.long`: commit date as `%B %d, %Y` (e.g. `April 12, 2026`)
    - `data.last_commit.dt.date.short`: commit date as `%Y-%m-%d` (e.g. `2026-04-12`)
    - `data.last_commit.dt.time`: commit time as `%H:%M:%S`
    - `data.last_commit.dt.iso`: commit datetime as ISO 8601

#### Regular page templates

- `page`
  - `page.active_page`: identifier derived from the filename (e.g. `about` for `about.html`, `home` for `index.html`), useful for highlighting the active nav item
  - `page.canonical_path`: URL path of the page (e.g. `/about`)
  - `page.content`: page content as HTML (only present if the page has front matter)
  - `page.metadata.<field>`: any front matter field (e.g. `page.metadata.title`)

#### Blog post template

- `post`: the current blog post
  - `post.title`: post title (from front matter, or derived from the filename)
  - `post.slug`: URL slug (filename without `.md`)
  - `post.content`: post body as HTML
  - `post.date`: date as `%Y-%m-%d` (e.g. `2026-04-12`), only set if a date is available
  - `post.date_iso`: date as ISO 8601, only set if a date is available
- `active_page`: name of the blog directory (e.g. `blog`)
- `canonical_path`: URL path of the post (e.g. `/blog/my-post`)
- `data`: same as above

#### Blog index template

- `posts`: list of all blog posts sorted newest first; each item has the same fields as `post` above
- `active_page`: name of the blog directory (e.g. `blog`)
- `canonical_path`: URL path of the blog index (e.g. `/blog`)
- `data`: same as above

## CLI

```bash
# Build with default config (stapler.toml)
stapler build

# Build with custom config
stapler build -c myconfig.toml

# Serve on default port (8000)
stapler serve

# Serve on custom port
stapler serve -p 3000

# Serve with custom config and port
stapler serve -c myconfig.toml -p 3000

# Show version
stapler --version
```
