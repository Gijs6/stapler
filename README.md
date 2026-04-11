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

Create a folder with `stapler.toml`:

```toml
[site]
url = "https://yoursite.com"
title = "Your site"
```

Those two fields are required, everything else is optional.

Stapler by default assumes your content is in the `site/` directory.

```bash
stapler serve
stapler build
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
base_path = "/blog"                # For deploying to example.com/blog instead of the root
```

#### Author info (used in rss/atom feeds)

```toml
[site.author]
name = "Your name"
email = "you@example.com"
```

#### Directories (all paths relative to where you run stapler)

```toml
[directories]
site = "site"                      # Where your content is (default: "site")
build = "build"                    # Production output (default: "build")
build_dev = "build-dev"            # Dev server output (default: "build-dev")
templates = "templates"            # Templates directory inside site directory (default: "templates")
blog = "blog"                      # Blog posts directory inside site directory (default: "blog")
```

#### Templates

```toml
[templates]
default = "base.html"              # Template used when page has no front matter
```

#### Blog

```toml
[features.blog]
enabled = true                     # Turn on blog functionality (default: false)
template = "blog_post.html"        # Template for individual posts
index_template = "blog_index.html" # Template for /blog/ index page
```

#### Other features

```toml
[features]
sitemap = true                     # Generate sitemap.xml (default: true)
feeds = true                       # Generate both rss.xml and atom.xml (only works if blog is enabled) (default: true)

[features.feeds]
rss = true                         # Generate rss.xml (default: true)
atom = true                        # Generate atom.xml (default: true)
```

#### Markdown processing

```toml
[markdown]
extensions = ["meta", "tables", "fenced_code"]  # Python-markdown extensions
```

## How it works

### Pages

Any `.html` or `.md` file in your site directory becomes a page.

**With front matter:**

```html
---
template: template.html
title: My page
custom_field: anything
---
<h1>Content here</h1>
```

```markdown
---
title: My page
---

# Content

Regular markdown here
```

The front matter is in YAML. All fields are avaiable as as `page.field_name` in your templates.

**Without front matter:**

Without front matter, the pages are treated as Jinja templates.

```html
{% extends "base.html" %}
{% block content %}
<h1>Hello</h1>
{% endblock %}
```

### Blog

If you enable the blog feature, put `.md` files in your blog directory.

```markdown
---
title: My post
date: 2025-01-15
---

Post content
```

The date is optional. If you don't provide it, stapler will try to get it from git history.

### Templates

Put templates in the directory you configured (default: `site/templates/`).

Templates get these variables:

- `data` - build info (current time, git commit, etc)
- `page` - page metadata and content (if page has front matter)
- `post` - blog post object (if it's a blog post)
- `posts` - all blog posts (sorted newest first)
- `active_page` - for nav highlighting
- `canonical_path` - url path

### Static files

Anything that's not in your templates or blog folder gets copied as-is.

## CLI

```bash
# build with default config (stapler.toml)
stapler build

# build with custom config
stapler build -c myconfig.toml

# serve on default port (8000)
stapler serve

# serve on custom port
stapler serve -p 3000

# serve with custom config and port
stapler serve -c myconfig.toml -p 3000

# show version
stapler --version
```
