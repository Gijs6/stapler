# stapler

a simple static site generator built with jinja2 and markdown. no fancy theme systems, just clean python code that turns your templates and content into a website.

## installation

clone the repo:

```bash
git clone https://github.com/gijs6/stapler.git
cd stapler
```

create a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate  # on windows: .venv\Scripts\activate
```

install:

```bash
pip install -e .
```

or with dev dependencies:

```bash
pip install -e ".[dev]"
```

## quick start

create a folder with `stapler.toml`:

```toml
[site]
url = "https://yoursite.com"
title = "your site"
```

those two fields are required. everything else is optional.

create a `site/` folder (or whatever you want to call it). put your content there. run:

```bash
stapler serve
```

that's it.

## configuration

### required

```toml
[site]
url = "https://yoursite.com"
title = "your site"
```

### optional stuff

**site metadata:**

```toml
[site]
description = "about your site"
base_path = "/blog"                # if deploying to example.com/blog instead of root
                                   # leave empty for root deployment
```

**author info** (used in rss/atom feeds):

```toml
[site.author]
name = "your name"
email = "you@example.com"
```

**directories** (all paths relative to where you run stapler):

```toml
[directories]
site = "site"                      # where your content lives (default: "site")
build = "build"                    # production output (default: "build")
build_dev = "build-dev"            # dev server output (default: "build-dev")
templates = "templates"            # templates folder inside site/ (default: "templates")
blog = "blog"                      # blog posts folder inside site/ (default: "blog")
```

**templates:**

```toml
[templates]
default = "base.html"              # template used when page has no front matter
```

**blog feature:**

```toml
[features.blog]
enabled = true                     # turn on blog functionality (default: false)
template = "blog_post.html"        # template for individual posts
index_template = "blog_index.html" # template for /blog/ index page
```

**other features:**

```toml
[features]
sitemap = true                     # generate sitemap.xml (default: true)
feeds = true                       # generate both rss.xml and atom.xml (default: true)
                                   # only works if blog is enabled

# or choose specific formats:
[features.feeds]
rss = true                         # generate rss.xml (default: true)
atom = true                        # generate atom.xml (default: true)
```

**markdown processing:**

```toml
[markdown]
extensions = ["meta", "tables", "fenced_code"]  # python-markdown extensions
                                                # meta = yaml front matter support
                                                # tables = markdown tables
                                                # fenced_code = ``` code blocks
```

## how it works

### pages

any `.html` or `.md` file in your site folder becomes a page.

**with front matter:**

```html
---
template: whatever.html
title: my page
custom_field: whatever you want
---
<h1>content here</h1>
```

front matter is yaml. you can put whatever fields you want in there. they'll be available as `page.field_name` in your templates.

**without front matter:**

treated as a jinja2 template. you can use template inheritance, variables, whatever.

```html
{% extends "base.html" %}
{% block content %}
<h1>hello</h1>
{% endblock %}
```

### markdown

works the same as html pages:

```markdown
---
title: my page
---

# content

regular markdown here
```

### blog

if you enable the blog feature, put `.md` files in your blog folder.

```markdown
---
title: my post
date: 2025-01-15
---

post content
```

date is optional - if you don't provide it, stapler tries to get it from git history.

### templates

put templates wherever you configured (default: `site/templates/`).

templates get these variables:

- `data` - build info (current time, git commit, etc)
- `page` - page metadata and content (if page has front matter)
- `post` - blog post object (if it's a blog post)
- `posts` - all blog posts (sorted newest first)
- `active_page` - for nav highlighting
- `canonical_path` - url path

structure them however you want. use template inheritance, partials, whatever jinja2 supports.

### static files

anything that's not in your templates or blog folder gets copied as-is. put your css, images, whatever wherever you want.

## cli

### commands

**build** - build your site for production

```bash
stapler build
```

options:

- `-c, --config FILE` - path to config file (default: stapler.toml)

**serve** - start dev server with live reload

```bash
stapler serve
```

options:

- `-c, --config FILE` - path to config file (default: stapler.toml)
- `-p, --port PORT` - port to serve on (default: 8000)

**general options**

- `--version` - show version and exit

### examples

```bash
# build with default config
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

## examples

a minimal site:

```
my-site/
├── stapler.toml
└── site/
    └── index.html
```

a blog:

```
my-site/
├── stapler.toml
└── site/
    ├── templates/
    │   ├── base.html
    │   ├── blog_post.html
    │   └── blog_index.html
    ├── blog/
    │   ├── first-post.md
    │   └── second-post.md
    └── index.html
```

organize it however makes sense to you.
