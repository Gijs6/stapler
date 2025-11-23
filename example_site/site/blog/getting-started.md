---
title: getting started
date: 2025-01-16
---

# getting started with stapler

here's how to get started with your own stapler site.

## create a config

create `stapler.toml`:

```toml
[site]
url = "https://yoursite.com"
title = "your site"
```

## add content

create a `site/` folder and put your content there. that's it!

## build

run `stapler build` to build your site, or `stapler serve` for a dev server.
